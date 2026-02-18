"""Main code definition for the conversion of a particular session type (raw or processed) to NWB."""

import pathlib
import typing

import pydantic
import warnings

import tqdm
import hdmf.build.warnings
import neuroconv.converters

from .interfaces import OdorIntervalsInterface, SpikeSortedInterface
from ..utils import enhance_metadata


@pydantic.validate_call
def odor_sequence_to_nwb(
    *,
    data_directory: pathlib.Path,
    subject_id: str | None = None,
    session_id: str | None = None,
    nwb_directory: pathlib.Path,
    raw_or_processed: typing.Literal["raw", "processed"],
    testing: bool = False,
    skip_if_exists: bool = True,
) -> None:
    """
    Convert a single session of raw or processed OdorSequence data to NWB.
    """
    if subject_id is not None and session_id is not None:
        subject_and_session_ids = [(subject_id, session_id)]
    else:
        subject_and_session_ids = [
            (subject_dir.stem, session_dir.stem.removeprefix(f"{subject_dir.stem}-"))
            for subject_dir in data_directory.iterdir()
            if subject_dir.is_dir()
            for session_dir in (subject_dir / "preprocessed").iterdir()
            if session_dir.is_dir()
        ]

    for subject_id, session_id in tqdm.tqdm(
        iterable=subject_and_session_ids, desc="Converting session(s)", unit="sessions", position=0, leave=True
    ):
        raw_data_directory = data_directory / subject_id / "rawdata" / f"{subject_id}-{session_id}_g0"
        preprocessed_data_directory = data_directory / subject_id / "preprocessed" / f"{subject_id}-{session_id}"
        filename = f"sub-{subject_id}_ses-{session_id}_ecephys.nwb"

        progress_bar_options = {"position": 1, "leave": False}
        conversion_options = {
            "stub_test": testing,
            "iterator_options": {"display_progress": True, "progress_bar_options": progress_bar_options},
        }
        nwbfile = None
        match raw_or_processed:
            case "raw":
                nwbfile_path = (
                    nwb_directory
                    / "sourcedata"
                    / f"sub-{subject_id}"
                    / f"ses-{session_id.replace("-", "+")}"
                    / filename
                )
                if skip_if_exists and nwbfile_path.exists():
                    return

                spikeglx_converter = neuroconv.converters.SpikeGLXConverterPipe(folder_path=raw_data_directory)

                metadata = spikeglx_converter.get_metadata()
                enhance_metadata(
                    metadata=metadata,
                    preprocessed_data_directory=preprocessed_data_directory,
                    spikeglx_converter=spikeglx_converter,
                )

                conversion_options = {
                    "imec0.ap": conversion_options,
                    "imec1.ap": conversion_options,
                    "nidq": conversion_options,
                }
                nwbfile = spikeglx_converter.create_nwbfile(metadata=metadata, conversion_options=conversion_options)
            case "processed":
                # spikeglx_converter = neuroconv.converters.SpikeGLXConverterPipe(folder_path=raw_data_directory)
                #
                # metadata = spikeglx_converter.get_metadata()
                nwbfile_path = (
                    nwb_directory
                    / "derivatives"
                    / f"sub-{subject_id}"
                    / f"ses-{session_id.replace("-", "+")}"
                    / filename
                )
                if skip_if_exists and nwbfile_path.exists():
                    return

                metadata = neuroconv.utils.DeepDict()
                enhance_metadata(
                    metadata=metadata,
                    preprocessed_data_directory=preprocessed_data_directory,
                    # spikeglx_converter=spikeglx_converter,
                )

                odor_interface = OdorIntervalsInterface(preprocessed_data_directory=preprocessed_data_directory)

                try:
                    nwbfile = odor_interface.create_nwbfile(metadata=metadata)
                except Exception as e:
                    message = f"Something went wrong while creating the NWB file from the odor interface: {e}"
                    raise ValueError(message)

                spike_sorted_interface = SpikeSortedInterface(preprocessed_data_directory=preprocessed_data_directory)
                spike_sorted_interface.add_to_nwbfile(nwbfile=nwbfile)

        if nwbfile is None:
            message = "Something went wrong while creating the NWB file."
            raise ValueError(message)

        # Suppress meaningless PyNWB warnings
        warnings.filterwarnings(
            action="ignore",
            message=r".*TimeIntervals/.*_time.*",
            category=hdmf.build.warnings.DtypeConversionWarning,
        )

        backend_configuration = neuroconv.tools.nwb_helpers.get_default_backend_configuration(
            nwbfile=nwbfile, backend="hdf5"
        )

        nwbfile_path.parent.mkdir(parents=True, exist_ok=True)
        neuroconv.tools.nwb_helpers.configure_and_write_nwbfile(
            nwbfile=nwbfile, nwbfile_path=nwbfile_path, backend_configuration=backend_configuration
        )
