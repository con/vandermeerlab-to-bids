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
        unit_ids = numpy.empty(shape=total_number_of_units, dtype="U9")
        depths = numpy.empty(shape=total_number_of_units, dtype="float64")
        shank_ids = numpy.empty(shape=total_number_of_units, dtype="uint8")
        channel_ids = numpy.empty(shape=total_number_of_units, dtype="U14")  # TODO: should be electrodes
        spike_times_by_unit_id: dict[str, np.ndarray] = dict()
        for probe_index, data_per_probe in enumerate(spike_sorted_arrays.values()):
            start_index = number_of_units_cumulative[probe_index]
            stop_index = number_of_units_cumulative[probe_index + 1]

            unit_ids[start_index:stop_index] = data_per_probe["unit_ids"]
            depths[start_index:stop_index] = data_per_probe["depths"]
            shank_ids[start_index:stop_index] = data_per_probe["shank_ids"].astype("uint8")
            channel_ids[start_index:stop_index] = data_per_probe["channel_ids"]

            for unit_id, spike_train in zip(data_per_probe["unit_ids"], data_per_probe["spike_train"]):
                spike_times_by_unit_id[unit_id] = spike_train

        sampling_frequency = 30000.0  # Hard-coded to match SpikeGLX probe
        BaseSorting.__init__(self, sampling_frequency=sampling_frequency, unit_ids=unit_ids)
        sorting_segment = VanDerMeerSortingSegment(
            sampling_frequency=sampling_frequency, spike_times_by_unit_id=spike_times_by_unit_id
        )
        self.add_sorting_segment(sorting_segment)

        self.set_property(key="relative_depth", values=depths)
        self.set_property(key="shank_id", values=shank_ids)
        self.set_property(key="channel_id", values=channel_ids)
        # self.set_property(
        #     key="mean_waveform",
        #     values=data_per_probe["mean_waveforms"],
        #     # ids=list(nwb_ids_by_unit_id.values()),
        # )


class VanDerMeerSortingSegment(spikeinterface.BaseSortingSegment):
    def __init__(self, sampling_frequency: float, spike_times_by_unit_id: Dict[int, np.ndarray]):
        super().__init__(self)
        self._t_start = 0.0
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
