"""Main conversion script for a single session."""

import pathlib

import vandermeerlab_to_bids.manish_2025

# TESTING=True creates 'preview' files that truncate all major data blocks; useful for ensuring process runs smoothly
TESTING = True

# TESTING=False performs a full file conversion
# TESTING = False


# Define base folder of source data
# Change these as needed on new systems
DATA_DIRECTORY = pathlib.Path("G:/") / "mvdm" / "Task2_SWR"
SUBJECT_ID = "M540"
SESSION_ID = "2024-08-16"


OUTPUT_DIRECTORY = pathlib.Path("E:/") / "mvdm" / "001470"
OUTPUT_DIRECTORY.mkdir(parents=True, exist_ok=True)


if __name__ == "__main__":
    # vandermeerlab_to_bids.manish_2025.odor_sequence_to_bids(
    #     data_directory=DATA_DIRECTORY,
    #     subject_id=SUBJECT_ID,
    #     session_id=SESSION_ID,
    #     bids_directory=BIDS_DIRECTORY,
    #     testing=TESTING,
    # )
    vandermeerlab_to_bids.manish_2025.odor_sequence_to_nwb(
        data_directory=DATA_DIRECTORY,
        subject_id=SUBJECT_ID,
        session_id=SESSION_ID,
        nwb_directory=OUTPUT_DIRECTORY,
        raw_or_processed="processed",
        testing=TESTING,
    )
