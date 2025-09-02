import neuroconv
import pydantic
from ._spike_sorting_extractor import VanDerMeerSortingExtractor


class SpikeSortedInterface(
    neuroconv.datainterfaces.ecephys.basesortingextractorinterface.BaseSortingExtractorInterface
):
    """Interface for handling spike sorted in the Manish 2025 OdorSequence dataset."""

    Extractor = VanDerMeerSortingExtractor

    @pydantic.validate_call
    def __init__(self, preprocessed_data_directory: pydantic.DirectoryPath) -> None:
        super().__init__(preprocessed_data_directory=preprocessed_data_directory)

    def get_metadata(self) -> dict:
        metadata = super().get_metadata()

        # TODO: add custom column descriptions

        return metadata
