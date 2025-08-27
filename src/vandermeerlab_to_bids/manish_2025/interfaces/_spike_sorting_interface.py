import neuroconv
import pydantic
import pynwb
import pymatreader
import pathlib
import typing
from ...utils import read_experiment_keys_file
from ._spike_sorting_extractor import VanDerMeerSortingExtractor


class SpikeSortedInterface(
    neuroconv.datainterfaces.ecephys.basesortingextractorinterface.BaseSortingExtractorInterface
):
    """Interface for handling spike sorted in the Manish 2025 OdorSequence dataset."""

    Extractor = VanDerMeerSortingExtractor

    @pydantic.validate_call
    def __init__(self, preprocessed_data_directory: pydantic.DirectoryPath) -> None:
        super().__init__(preprocessed_data_directory=preprocessed_data_directory)
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

    def add_to_nwbfile(
        self, nwbfile: pynwb.NWBFile, metadata: dict | None = None, conversion_options: dict | None = None
    ) -> None:
        """Add spike sorted data to the NWBFile."""
        for file_path, spike_sorted_array in self.spike_sorted_arrays.items():
            probe_number = file_path.stem[-1]
            probe_id = f"imec{probe_number}"
            print(probe_id)
