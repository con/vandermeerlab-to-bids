from collections import defaultdict
from typing import Dict, Union
import typing
import pathlib
import numpy as np
import pydantic
from spikeinterface import BaseSorting
import pymatreader
import spikeinterface
import numpy
from ...utils import read_experiment_keys_file


class VanDerMeerSortingExtractor(spikeinterface.BaseSorting):
    extractor_name = "VanDerMeerSorting"
    installed = True
    mode = "file"
    installation_mesg = ""
    name = "vandermeersorting"

    def __init__(self, preprocessed_data_directory: pydantic.DirectoryPath):
        self.preprocessed_data_directory = preprocessed_data_directory

        session_id = self.preprocessed_data_directory.name
        experiment_keys_file_name = f"{session_id.replace('-', '_')}_keys.m"
        experiment_keys_file_path = self.preprocessed_data_directory / experiment_keys_file_name
        self.experiment_keys = read_experiment_keys_file(file_path=experiment_keys_file_path)

        self.clean_spike_sorted_file_paths: list[pathlib.Path] = list(
            self.preprocessed_data_directory.glob(pattern="clean_units_imec*.mat")
        )
        self.spike_sorted_arrays: dict[pathlib.Path, dict[str, typing.Any]] = {
            file_path: pymatreader.read_mat(filename=file_path) for file_path in self.clean_spike_sorted_file_paths
        }

        all_unit_properties = dict()
        spike_times_by_id = defaultdict(list)  # Cast lists per key as arrays after assembly
        spike_depths_by_id = defaultdict(list)
        unit_id_per_probe_shift = 0
        for file_path, data_per_probe in self.spike_sorted_arrays.items():
            probe_name = file_path.stem[-5]

            spikes: list[numpy.ndarray] = data_per_probe["spike_train"]
            print(spikes)
            channels: numpy.ndarray = data_per_probe["channel_ids"]
            print(channels)

            number_of_units = len(np.unique(spikes["clusters"]))

            # TODO - add waveforms as separate interface
            for spike_cluster, spike_times, spike_amplitudes, spike_depths in zip(
                spikes["clusters"], spikes["times"], spikes["amps"], spikes["depths"]
            ):
                unit_id = unit_id_per_probe_shift + spike_cluster
                spike_times_by_id[unit_id].append(spike_times)
                spike_depths_by_id[unit_id].append(spike_depths)

            unit_id_per_probe_shift += number_of_units
            all_unit_properties["probe_name"].extend([probe_name] * number_of_units)

        for unit_id in spike_times_by_id:  # Cast as arrays for fancy indexing
            spike_times_by_id[unit_id] = spike_times_by_id[unit_id]

        sampling_frequency = 30000.0  # Hard-coded to match SpikeGLX probe
        BaseSorting.__init__(self, sampling_frequency=sampling_frequency, unit_ids=list(spike_times_by_id.keys()))
        sorting_segment = VanDerMeerSortingSegment(
            sampling_frequency=sampling_frequency,
            spike_times_by_id=spike_times_by_id,
        )
        self.add_sorting_segment(sorting_segment)

        self.set_property(
            key="spike_relative_depths",
            values=np.array(list(spike_depths_by_id.values()), dtype=object),
            ids=list(spike_depths_by_id.keys()),
        )

        for property_name, values in all_unit_properties.items():
            self.set_property(key=property_name, values=values, ids=list(spike_depths_by_id.keys()))


class VanDerMeerSortingSegment(spikeinterface.BaseSortingSegment):
    def __init__(self, sampling_frequency: float, spike_times_by_id: Dict[int, np.ndarray]):
        super().__init__(self)
        self._sampling_frequency = sampling_frequency
        self._spike_times_by_id = spike_times_by_id

    def get_unit_spike_train(
        self,
        unit_id: int,
        start_frame: Union[int, None] = None,
        end_frame: Union[int, None] = None,
    ) -> np.ndarray:
        times = np.array(self._spike_times_by_id[unit_id])  # Make a copy for possible mutation below
        frames = (times * self._sampling_frequency).astype(int)
        if start_frame is not None:
            frames = frames[frames >= start_frame]
        if end_frame is not None:
            frames = frames[frames < end_frame]
        return frames
