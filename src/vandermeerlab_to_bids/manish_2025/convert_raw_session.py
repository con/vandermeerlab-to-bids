"""Main conversion script for a single session of raw ephys data."""

import pathlib

from vandermeerlab_to_bids.manish_2025 import odor_sequence_to_bids

# TESTING=True creates 'preview' files that truncate all major data blocks; useful for ensuring process runs smoothly
TESTING = True

# TESTING=False performs a full file conversion
# TESTING = False


# Define base folder of source data
# Change these as needed on new systems
DATA_DIRECTORY = pathlib.Path("E:/") / "bids_32_examples" / "mvdm" / "OdorSequence" / "sourcedata"
SUBJECT_ID = "M541"
SESSION_ID = "2024-08-31"


BIDS_DIRECTORY = DATA_DIRECTORY / "bids"
BIDS_DIRECTORY.mkdir(exist_ok=True)


if __name__ == "__main__":
    odor_sequence_to_bids(
        data_directory=DATA_DIRECTORY,
        subject_id=SUBJECT_ID,
        session_id=SESSION_ID,
        bids_directory=BIDS_DIRECTORY,
        raw_or_processed="raw",
        testing=TESTING,
    )
