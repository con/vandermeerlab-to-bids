"""Debugging script for a single session."""

import pathlib

import vandermeerlab_to_bids.manish_2025

DATA_DIRECTORY = pathlib.Path("G:/") / "mvdm" / "Task2_SWR"
SUBJECT_ID = "M540"
SESSION_ID = "2024-08-19"


OUTPUT_DIRECTORY = pathlib.Path("D:/") / "mvdm" / "001470"
OUTPUT_DIRECTORY.mkdir(parents=True, exist_ok=True)


if __name__ == "__main__":
    vandermeerlab_to_bids.manish_2025.odor_sequence_to_nwb(
        data_directory=DATA_DIRECTORY,
        subject_id=SUBJECT_ID,
        session_id=SESSION_ID,
        nwb_directory=OUTPUT_DIRECTORY,
        raw_or_processed="raw",
        testing=True,
        skip_if_exists=False,
    )
