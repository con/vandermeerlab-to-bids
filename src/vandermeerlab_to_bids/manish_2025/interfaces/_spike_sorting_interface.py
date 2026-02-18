import neuroconv
import pydantic
from ._spike_sorting_extractor import VanDerMeerSortingExtractor


class SpikeSortedInterface(
    neuroconv.datainterfaces.ecephys.basesortingextractorinterface.BaseSortingExtractorInterface
):
    """Interface for handling spike sorted in the Manish 2025 OdorSequence dataset."""

    @pydantic.validate_call
    def __init__(self, preprocessed_data_directory: pydantic.DirectoryPath) -> None:
        super().__init__(preprocessed_data_directory=preprocessed_data_directory)

    def get_metadata(self) -> dict:
        metadata = super().get_metadata()

        metadata["Ecephys"]["UnitProperties"] = [
            {
                "name": "relative_depth",
                "description": "The depth (in microns) of the unit relative to the insertion point.",
            },
            {"name": "shank_id", "description": "The shank the unit was detected on."},
            {"name": "channel_id", "description": "The identifier of the closest channel to the unit."},
        ]

        return metadata

    @classmethod
    def get_extractor_class(cls):
        return VanDerMeerSortingExtractor
