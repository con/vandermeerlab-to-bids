import warnings
from typing import Dict, Union
import typing
import pathlib
import numpy as np
import pydantic
from spikeinterface import BaseSorting
import pymatreader
import spikeinterface
import numpy


class VanDerMeerSortingExtractor(spikeinterface.BaseSorting):
    extractor_name = "VanDerMeerSorting"
    installed = True
    mode = "file"
    installation_mesg = ""
    name = "vandermeersorting"

    def __init__(self, preprocessed_data_directory: pydantic.DirectoryPath):
        clean_spike_sorted_file_paths: list[pathlib.Path] = list(
            preprocessed_data_directory.glob(pattern="clean_units_imec*.mat")
        )
        spike_sorted_arrays: dict[pathlib.Path, dict[str, typing.Any]] = {
            file_path: pymatreader.read_mat(filename=file_path) for file_path in clean_spike_sorted_file_paths
        }

        number_of_units_per_probe = [
            data_per_probe["unit_ids"].shape[0] for data_per_probe in spike_sorted_arrays.values()
        ]
        total_number_of_units = sum(number_of_units_per_probe)

        number_of_units_cumulative = numpy.cumsum([0] + number_of_units_per_probe)
        number_of_waveform_frames = next(iter(spike_sorted_arrays.values()))["mean_waveforms"][0].shape[1]
        max_number_of_waveform_channels = max(
            [
                mean_waveform.shape[0]
                for data_per_probe in spike_sorted_arrays.values()
                for mean_waveform in data_per_probe["mean_waveforms"]
            ]
        )

        unit_ids = numpy.empty(shape=total_number_of_units, dtype="U9")
        depths = numpy.empty(shape=total_number_of_units, dtype="float64")
        shank_ids = numpy.empty(shape=total_number_of_units, dtype="uint8")
        channel_ids = numpy.empty(shape=total_number_of_units, dtype="U14")  # TODO: should be electrodes
        waveform_means = numpy.full(
            shape=(total_number_of_units, number_of_waveform_frames, max_number_of_waveform_channels),
            fill_value=numpy.nan,
        )
        spike_times_by_unit_id: dict[str, np.ndarray] = dict()
        for probe_index, data_per_probe in enumerate(spike_sorted_arrays.values()):
            start_index = number_of_units_cumulative[probe_index]
            stop_index = number_of_units_cumulative[probe_index + 1]

            unit_ids[start_index:stop_index] = data_per_probe["unit_ids"]
            depths[start_index:stop_index] = data_per_probe["depths"]
            shank_ids[start_index:stop_index] = data_per_probe["shank_ids"].astype("uint8")
            channel_ids_per_probe = data_per_probe.get("channel_ids", None)
            if channel_ids_per_probe is not None:
                channel_ids[start_index:stop_index] = channel_ids_per_probe

            for unit_id, spike_train in zip(data_per_probe["unit_ids"], data_per_probe["spike_train"]):
                spike_times_by_unit_id[unit_id] = spike_train

            for unit_index_per_probe, waveforms in enumerate(data_per_probe["mean_waveforms"]):
                unit_index = start_index + unit_index_per_probe
                num_channels, num_frames = waveforms.shape
                waveform_means[unit_index, :num_frames, :num_channels] = waveforms.T

        sampling_frequency = 30000.0  # Hard-coded to match SpikeGLX probe
        BaseSorting.__init__(self, sampling_frequency=sampling_frequency, unit_ids=unit_ids)
        sorting_segment = VanDerMeerSortingSegment(
            sampling_frequency=sampling_frequency, spike_times_by_unit_id=spike_times_by_unit_id
        )
        self.add_sorting_segment(sorting_segment)

        self.set_property(key="relative_depth", values=depths)
        self.set_property(key="shank_id", values=shank_ids)

        warnings.filterwarnings(
            action="ignore", message="Column 'waveform_mean' is predefined*", category=UserWarning, module="neuroconv"
        )
        warnings.filterwarnings(action="ignore", message="Shape of data does not match*", module="hdmf")
        self.set_property(key="waveform_mean", values=waveform_means)

        if any(channel_ids):
            self.set_property(key="channel_id", values=channel_ids)


class VanDerMeerSortingSegment(spikeinterface.BaseSortingSegment):
    def __init__(self, sampling_frequency: float, spike_times_by_unit_id: Dict[int, np.ndarray]):
        super().__init__()
        self._sampling_frequency: float = sampling_frequency
        self._spike_times_by_unit_id: dict[int, np.ndarray] = spike_times_by_unit_id

    def get_unit_spike_train(
        self,
        unit_id: int,
        start_frame: Union[int, None] = None,
        end_frame: Union[int, None] = None,
    ) -> np.ndarray:
        times = np.array(self._spike_times_by_unit_id[unit_id])
        frames = (times * self._sampling_frequency).astype(int)
        if start_frame is not None:
            frames = frames[frames >= start_frame]
        if end_frame is not None:
            frames = frames[frames < end_frame]
        return frames
