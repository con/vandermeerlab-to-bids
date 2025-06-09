import typing

import neuroconv
import pydantic
import pynwb
import re

from ...utils import read_experiment_keys_file


class OdorIntervalsInterface(neuroconv.BaseDataInterface):
    """Interface for handling odor intervals in the Manish 2025 OdorSequence dataset."""

    @pydantic.validate_call
    def __init__(self, preprocessed_data_directory: pydantic.DirectoryPath) -> None:
        super().__init__(preprocessed_data_directory=preprocessed_data_directory)
        self.preprocessed_data_directory = preprocessed_data_directory

        session_id = self.preprocessed_data_directory.name
        experiment_keys_file_name = f"{session_id.replace('-', '_')}_keys.m"
        experiment_keys_file_path = self.preprocessed_data_directory / experiment_keys_file_name
        self.experiment_keys = read_experiment_keys_file(file_path=experiment_keys_file_path)
        self.odor_ids = _get_odor_ids(keys=self.experiment_keys)
        self.block_ids = _get_block_ids(keys=self.experiment_keys)

    def add_to_nwbfile(
        self, nwbfile: pynwb.NWBFile, metadata: dict | None = None, conversion_options: dict | None = None
    ) -> None:
        """Add odor intervals to the NWBFile."""
        odor_sequences = pynwb.epoch.TimeIntervals(
            name="trials",
            description="The on/off timing of presented odors IDs. See experiment description for details on chemical compositions of each odor.",
        )
        odor_sequences.add_column(name="odor_id", description="The odor ID that was presented during this trial.")

        blocks = pynwb.epoch.TimeIntervals(
            name="epochs",
            description="Each block in this experiment involves a specific repetition of a subset of odor IDs. See experiment description for details on odor combinations per block.",
        )
        blocks.add_column(name="block_id", description="The block ID that was presented during this epoch.")

        all_trials = []
        for odor_id in self.odor_ids:
            channel_name = self.experiment_keys[f"odor{odor_id}_channel"]

            on_channel_file_path = self.preprocessed_data_directory / f"{channel_name}_ON.txt"
            off_channel_file_path = self.preprocessed_data_directory / f"{channel_name}_OFF.txt"

            with on_channel_file_path.open("r") as on_file_stream, off_channel_file_path.open("r") as off_file_stream:
                all_trials.extend(
                    [
                        {"start_time": float(on_time), "stop_time": float(off_time), "odor_id": odor_id}
                        for on_time, off_time in zip(on_file_stream, off_file_stream)
                    ]
                )

        all_trials.sort(key=lambda row: row["start_time"])
        for row in all_trials:
            odor_sequences.add_row(start_time=row["start_time"], stop_time=row["stop_time"], odor_id=row["odor_id"])

        all_epochs = []
        for block_id in self.block_ids:
            block_start_key = f"block{block_id}start"
            block_end_key = f"block{block_id}end"

            start_time = self.experiment_keys[block_start_key]
            stop_time = self.experiment_keys[block_end_key]
            all_epochs.append({"start_time": start_time, "stop_time": stop_time, "block_id": block_id})

        all_epochs.sort(key=lambda row: row["start_time"])
        for row in all_epochs:
            blocks.add_row(start_time=row["start_time"], stop_time=row["stop_time"], block_id=row["block_id"])

        nwbfile.trials = odor_sequences
        nwbfile.epochs = blocks


def _get_odor_ids(keys: typing.Iterable[str]) -> list[str]:
    """Rather than hard-coding the odor types, we will extract them from the experiment keys."""
    pattern = r"odor([A-Z])_channel"

    matches = [result.group(1) for key in keys if (result := re.match(pattern=pattern, string=key)) is not None]
    return matches


def _get_block_ids(keys: typing.Iterable[str]) -> list[str]:
    """Extract block IDs from the experiment keys."""
    pattern = r"block(\d+)_type"

    matches = [result.group(1) for key in keys if (result := re.match(pattern=pattern, string=key)) is not None]
    return matches
