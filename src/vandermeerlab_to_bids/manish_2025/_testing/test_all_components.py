"""
Test each individual interface by performing standalone file creations.

An actual conversion should use the `convert_*.py` scripts.

This just makes debugging easier.
"""

import pathlib
import warnings
import neuroconv.converters
import pynwb
import vandermeerlab_to_bids.utils
import pynwb.testing.mock.file

import vandermeerlab_to_bids
import vandermeerlab_to_bids.manish_2025

# Define base folder of source data
# Change these as needed on new systems
BASE_DIRECTORY = pathlib.Path("E:/bids_32_examples") / "mvdm" / "OdorSequence" / "sourcedata"
SUBJECT_ID = "M541"
SESSION_ID = "2024-08-31"

BIDS_DIRECTORY = BASE_DIRECTORY / "bids"
BIDS_DIRECTORY.mkdir(exist_ok=True)

# *************************************************************************
# Everything below this line is automated and should not need to be changed
# *************************************************************************

# Suppress false warning
warnings.filterwarnings(action="ignore", message="The linked table for DynamicTableRegion*", category=UserWarning)

BIDS_DIRECTORY.mkdir(exist_ok=True)
test_folder_path = BIDS_DIRECTORY / "test_components"
test_folder_path.mkdir(exist_ok=True)

# Parse session start time from the pumpprobe path
raw_data_directory = BASE_DIRECTORY / "raw" / SUBJECT_ID / f"{SUBJECT_ID}-{SESSION_ID}_g0"
processed_data_directory = BASE_DIRECTORY / "preprocessed" / SUBJECT_ID / f"{SUBJECT_ID}-{SESSION_ID}"

components_to_test = {
    neuroconv.converters.SpikeGLXConverterPipe: {
        "source_data": {"folder_path": raw_data_directory},
        "conversion_options": {
            "imec0.ap": {"stub_test": True},
            "imec1.ap": {"stub_test": True},
            "nidq": {"stub_test": True},
        },
    },
}

for component_to_test, component_options in components_to_test.items():
    source_data = component_options["source_data"]
    conversion_options = component_options.get("conversion_options", None)

    converter = component_to_test(**source_data)

    metadata = converter.get_metadata()
    vandermeerlab_to_bids.utils.enhance_metadata(metadata=metadata, directory_path=processed_data_directory)

    in_memory_nwbfile = pynwb.testing.mock.file.mock_NWBFile()
    converter.add_to_nwbfile(nwbfile=in_memory_nwbfile, metadata=metadata, conversion_options=conversion_options)

    print("Added to in-memory NWBFile object!")

    nwbfile_path = test_folder_path / f"test_{component_to_test.__name__}.nwb"
    converter.run_conversion(
        nwbfile_path=nwbfile_path, metadata=metadata, conversion_options=conversion_options, overwrite=True
    )

    # Test roundtrip to make sure PyNWB can read the file back
    with pynwb.NWBHDF5IO(path=nwbfile_path, mode="r") as io:
        read_nwbfile = io.read()
