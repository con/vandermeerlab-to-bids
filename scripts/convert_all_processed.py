"""Main conversion script for a single session."""

import pathlib

import vandermeerlab_to_bids.manish_2025

DATA_DIRECTORY = pathlib.Path("G:/") / "mvdm" / "Task2_SWR"
# DATA_DIRECTORY = pathlib.Path("D:/") / "mvdm" / "conversion" / "input"

OUTPUT_DIRECTORY = pathlib.Path("E:/") / "mvdm" / "001470"
OUTPUT_DIRECTORY.mkdir(parents=True, exist_ok=True)


if __name__ == "__main__":
    vandermeerlab_to_bids.manish_2025.odor_sequence_to_nwb(
        data_directory=DATA_DIRECTORY,
        nwb_directory=OUTPUT_DIRECTORY,
        raw_or_processed="processed",
        skip_if_exists=False,
    )
