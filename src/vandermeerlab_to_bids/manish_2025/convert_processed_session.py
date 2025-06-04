"""Main conversion script for a single session of processed data."""

import pathlib


from vandermeerlab_to_bids.manish_2025 import odor_sequence_to_bids

# TESTING=True creates 'preview' files that truncate all major data blocks; useful for ensuring process runs smoothly
# TESTING = True

# TESTING=False performs a full file conversion
TESTING = False


# Define base folder of source data
# Change these as needed on new systems
DATA_DIRECTORY = pathlib.Path("D:/mvdm")
SUBJECT_ID = "M541"

OUTPUT_FOLDER_PATH = pathlib.Path("E:/mvdm")
BIDS_DIRECTORY = OUTPUT_FOLDER_PATH / "bids"
BIDS_DIRECTORY.mkdir(exist_ok=True)


if __name__ == "__main__":
    odor_sequence_to_bids(
        data_directory=DATA_DIRECTORY,
        subject_info_file_path=SUBJECT_INFO_FILE_PATH,
        subject_id=SUBJECT_ID,
        bids_directory=BIDS_DIRECTORY,
        raw_or_processed="processed",
        testing=TESTING,
    )
