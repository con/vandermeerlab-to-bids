"""Main code definition for the conversion of a particular session type (raw or processed) to NWB."""

import typing

import pydantic
import warnings

import hdmf.build.warnings
import neuroconv.converters
import pynwb
import pynwb.testing.mock.file

from .interfaces import OdorIntervalsInterface, SpikeSortedInterface
from ..utils import enhance_metadata


@pydantic.validate_call
def odor_sequence_to_nwb(
    *,
    data_directory: pydantic.DirectoryPath,
    subject_id: str,
    session_id: str,
    nwb_directory: pydantic.DirectoryPath,
    raw_or_processed: typing.Literal["raw", "processed", "both"],
    testing: bool = False,
) -> None:
    """
    Convert a single session of OdorSequence data to NWB.

    Expected to be structured similar to...

    |- OdorSequence
    |--- sourcedata
    |----- preprocessed
    |------- < subject ID >
    |--------- < subject ID >-< session ID >
    |----- raw
    |------- < subject ID >
    |--------- < subject ID >-< session ID >_< SpikeGLX gate >

    For example...

    |- OdorSequence
    |--- sourcedata
    |----- preprocessed
    |------- M541
    |--------- M541-2024-08-31
    |----- raw
    |------- M541
    |--------- M541-2024-08-31_g0
    """
    raw_data_directory = data_directory / "raw" / subject_id / f"{subject_id}-{session_id}_g0"
    preprocessed_data_directory = data_directory / "preprocessed" / subject_id / f"{subject_id}-{session_id}"

    modalities = "ecephys" if raw_or_processed == "raw" else "ecephys+behavior"
    filename = f"sub-{subject_id}_ses-{session_id}_desc-{raw_or_processed}_{modalities}.nwb"
    nwbfile_path = nwb_directory / f"sub-{subject_id}" / f"ses-{session_id}" / filename
    nwbfile_path.parent.mkdir(parents=True, exist_ok=True)

    nwbfile = None
    match raw_or_processed:
        case "raw":
            spikeglx_converter = neuroconv.converters.SpikeGLXConverterPipe(folder_path=raw_data_directory)

            metadata = spikeglx_converter.get_metadata()
            enhance_metadata(
                metadata=metadata,
                preprocessed_data_directory=preprocessed_data_directory,
                spikeglx_converter=spikeglx_converter,
            )

            conversion_options = {
                "imec0.ap": {"stub_test": testing},
                "imec1.ap": {"stub_test": testing},
                "nidq": {"stub_test": testing},
            }
            nwbfile = spikeglx_converter.create_nwbfile(metadata=metadata, conversion_options=conversion_options)
        case "processed":
            spikeglx_converter = neuroconv.converters.SpikeGLXConverterPipe(folder_path=raw_data_directory)

            metadata = spikeglx_converter.get_metadata()
            enhance_metadata(
                metadata=metadata,
                preprocessed_data_directory=preprocessed_data_directory,
                spikeglx_converter=spikeglx_converter,
            )

            odor_interface = OdorIntervalsInterface(preprocessed_data_directory=preprocessed_data_directory)
            nwbfile = odor_interface.create_nwbfile(metadata=metadata)

            spike_sorted_interface = SpikeSortedInterface(preprocessed_data_directory=preprocessed_data_directory)
            spike_sorted_interface.add_to_nwbfile(nwbfile=nwbfile)
        case "both":  # TODO: once nwb2bids supports multiple NWB files per session, remove this option
            spikeglx_converter = neuroconv.converters.SpikeGLXConverterPipe(folder_path=raw_data_directory)

            metadata = spikeglx_converter.get_metadata()
            enhance_metadata(
                metadata=metadata,
                preprocessed_data_directory=preprocessed_data_directory,
                spikeglx_converter=spikeglx_converter,
            )

            conversion_options = {
                "imec0.ap": {"stub_test": testing},
                "imec1.ap": {"stub_test": testing},
                "nidq": {"stub_test": testing},
            }
            nwbfile = spikeglx_converter.create_nwbfile(metadata=metadata, conversion_options=conversion_options)

            odor_interface = OdorIntervalsInterface(preprocessed_data_directory=preprocessed_data_directory)
            odor_interface.add_to_nwbfile(nwbfile=nwbfile)

            spike_sorted_interface = SpikeSortedInterface(preprocessed_data_directory=preprocessed_data_directory)
            spike_sorted_interface.add_to_nwbfile(
                nwbfile=nwbfile, units_description="Curated spike sorting data across all probes."
            )

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
