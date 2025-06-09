"""
Test each individual interface by performing standalone file creations.

An actual conversion should use the `convert_*.py` scripts.

This just makes debugging easier.
"""

import datetime
import pathlib
import warnings

import pynwb
from dateutil import tz
from pynwb.testing.mock.file import mock_NWBFile

from vandermeerlab_to_bids.manish_2025 import Manish2025Converter

# Define base folder of source data
# Change these as needed on new systems
DATA_DIRECTORY = pathlib.Path("E:/mvdm")
SUBJECT_ID = "M541"
SESSION_ID = "2024-08-31"

BIDS_DIRECTORY = DATA_DIRECTORY / "bids"
BIDS_DIRECTORY.mkdir(exist_ok=True)

# *************************************************************************
# Everything below this line is automated and should not need to be changed
# *************************************************************************

# Suppress false warning
warnings.filterwarnings(action="ignore", message="The linked table for DynamicTableRegion*", category=UserWarning)

BIDS_DIRECTORY.mkdir(exist_ok=True)
test_folder_path = BIDS_DIRECTORY / "test_interfaces"
test_folder_path.mkdir(exist_ok=True)

# Parse session start time from the pumpprobe path
session_string = PUMPPROBE_FOLDER_PATH.stem.removeprefix("pumpprobe_")
session_start_time = datetime.datetime.strptime(session_string, "%Y%m%d_%H%M%S")
session_start_time = session_start_time.replace(tzinfo=tz.gettz("US/Eastern"))

interfaces_classes_to_test = {
    # TODO
    # "PumpProbeImagingInterfaceGreen": {
    #     "source_data": {"pump_probe_folder_path": PUMPPROBE_FOLDER_PATH, "channel_name": "Green"},
    #     "conversion_options": {"stub_test": True},
    # },
}


for test_case_name, interface_options in interfaces_classes_to_test.items():
    source_data = {test_case_name: interface_options["source_data"]}
    converter = Manish2025Converter(source_data=source_data)

    metadata = converter.get_metadata()

    in_memory_nwbfile = mock_NWBFile()
    converter.add_to_nwbfile(nwbfile=in_memory_nwbfile, metadata=metadata, conversion_options=conversion_options)

    print("Added to in-memory NWBFile object!")

    nwbfile_path = test_folder_path / f"test_{test_case_name}.nwb"
    converter.run_conversion(
        nwbfile_path=nwbfile_path, metadata=metadata, conversion_options=conversion_options, overwrite=True
    )

    # Test roundtrip to make sure PyNWB can read the file back
    with pynwb.NWBHDF5IO(path=nwbfile_path, mode="r") as io:
        read_nwbfile = io.read()
