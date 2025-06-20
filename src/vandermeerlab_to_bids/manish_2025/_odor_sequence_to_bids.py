"""Main code definition for the conversion of a full session (including NeuroPAL)."""

import typing

import pydantic
import warnings

import hdmf.build.warnings
import neuroconv.converters
import pynwb
import pynwb.testing.mock.file

from .interfaces import OdorIntervalsInterface
from ..utils import enhance_metadata


@pydantic.validate_call
def odor_sequence_to_bids(
    *,
    data_directory: pydantic.DirectoryPath,
    subject_id: str,
    session_id: str,
    bids_directory: pydantic.DirectoryPath,
    raw_or_processed: typing.Literal["raw", "processed"],
    testing: bool = False,
) -> None:
    """Convert a single session of OdorSequence data to BIDS format."""
    raw_data_directory = data_directory / "raw" / subject_id / f"{subject_id}-{session_id}_g0"
    preprocessed_data_directory = data_directory / "preprocessed" / subject_id / f"{subject_id}-{session_id}"

    filename = f"sub-{subject_id}_ses-{session_id}_desc-{raw_or_processed}_ecephys+behavior.nwb"
    nwbfile_path = bids_directory.parent / "nwb" / f"sub-{subject_id}" / f"ses-{session_id}" / filename
    nwbfile_path.parent.mkdir(parents=True, exist_ok=True)

    nwbfile = None
    match raw_or_processed:
        case "raw":
            spikeglx_converter = neuroconv.converters.SpikeGLXConverterPipe(folder_path=raw_data_directory)

            metadata = spikeglx_converter.get_metadata()
            enhance_metadata(metadata=metadata, preprocessed_data_directory=preprocessed_data_directory)

            conversion_options = {
                "imec0.ap": {"stub_test": testing},
                "imec1.ap": {"stub_test": testing},
                "nidq": {"stub_test": testing},
            }
            nwbfile = spikeglx_converter.create_nwbfile(metadata=metadata, conversion_options=conversion_options)

            odor_interface = OdorIntervalsInterface(preprocessed_data_directory=preprocessed_data_directory)
            odor_interface.add_to_nwbfile(nwbfile=nwbfile)
        case "processed":
            if metadata["NWBFile"].get("session_start_time", None) is None:
                spikeglx_converter = neuroconv.converters.SpikeGLXConverterPipe(folder_path=raw_data_directory)
                spikeglx_metadata = spikeglx_converter.get_metadata()

                metadata["NWBFile"]["session_start_time"] = spikeglx_metadata["NWBFile"]["session_start_time"]

    if nwbfile is None:
        message = "Something went wrong while creating the NWB file."
        raise ValueError(message)

    # Suppress meaningless PyNWB warnings
    warnings.filterwarnings(
        action="ignore",
        message=r".*TimeIntervals/.*_time.*",
        category=hdmf.build.warnings.DtypeConversionWarning,
    )

    with pynwb.NWBHDF5IO(path=nwbfile_path, mode="w") as file_stream:
        file_stream.write(nwbfile)
