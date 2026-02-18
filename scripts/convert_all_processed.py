"""Main conversion script for a single session."""

import pathlib

import vandermeerlab_to_bids.manish_2025

DATA_DIRECTORY = pathlib.Path("E:/") / "mvdm" / "all_processed"

OUTPUT_DIRECTORY = pathlib.Path("E:/") / "mvdm" / "001470"
OUTPUT_DIRECTORY.mkdir(parents=True, exist_ok=True)


if __name__ == "__main__":
    for subject_dir in DATA_DIRECTORY.iterdir():
        if not subject_dir.is_dir():
            continue

        subject_id = subject_dir.stem

        session_dirs = DATA_DIRECTORY / subject_id / "preprocessed"
        for session_dir in session_dirs.iterdir():
            if not session_dir.is_dir():
                continue

            session_id = "-".join(session_dir.stem.split("-")[1:])

            print(f"Processing subject {subject_id}, session {session_id}...")
            vandermeerlab_to_bids.manish_2025.odor_sequence_to_nwb(
                data_directory=DATA_DIRECTORY,
                subject_id=subject_id,
                session_id=session_id,
                nwb_directory=OUTPUT_DIRECTORY,
                raw_or_processed="processed",
                skip_if_exists=False,
            )
