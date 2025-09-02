"""Main code definition for the conversion of a full session to BIDS."""

import pydantic

import nwb2bids

from ._odor_sequence_to_nwb import odor_sequence_to_nwb


@pydantic.validate_call
def odor_sequence_to_bids(
    *,
    data_directory: pydantic.DirectoryPath,
    subject_id: str,
    session_id: str,
    bids_directory: pydantic.DirectoryPath,
    testing: bool = False,
) -> None:
    """Organize a single session of OdorSequence data to BIDS."""
    nwb_directory = bids_directory.parent / "nwb"
    nwb_directory.mkdir(exist_ok=True)

    # for raw_or_processed in ["raw", "processed"]:  # TODO: once nwb2bids support multiple NWB files per session
    for raw_or_processed in ["both"]:
        odor_sequence_to_nwb(
            data_directory=data_directory,
            subject_id=subject_id,
            session_id=session_id,
            nwb_directory=nwb_directory,
            raw_or_processed=raw_or_processed,
            testing=testing,
        )

    nwb2bids.convert_nwb_dataset(
        nwb_paths=[nwb_directory],
        bids_directory=bids_directory,
    )
