import neuroconv
import numpy
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

    def add_to_nwbfile(
        self, nwbfile: pynwb.NWBFile, metadata: dict | None = None, conversion_options: dict | None = None
    ) -> None:
        """
        Add odor intervals to the NWBFile.

        Designed to be consistent with existing NWB datasets involving odor stimuli, such as Dandiset 001170.
        """
        # Olfactometer device (just for metadata)
        olfactometer_description = (
            "The olfactometer consists of different vials attached to a pressurized air system. "
            "Each vial contains a different odorant, which is mixed with mineral oil. "
            "Earlier sessions used USP-specification level M1180 mineral oil from Sigma-Aldrich "
            "(CAS: 8042-47-5; EC: 232-455-8; MDL: MFCD00131611; UNSPSC: 12181504; NACRES: NA.25). "
            "Later sessions used laboratory-grade 'heavy' mineral oil by ALDON Innovating Science "
            "(Item #: IS22096; ASIN: B0787CJJBJ). "
            "When a specific odor is being presented, air is passed through the vial containing that odorant. "
            "When the odor is not being presented, the vial with the pure mineral oil has air passing through "
            "it to cause washout of the previously delivered odor from the system."
        )
        device = pynwb.device.Device(name="Olfactometer", description=olfactometer_description)
        nwbfile.add_device(devices=device)

        # Odor sequences (trials)
        odor_ids = self._get_odor_ids()

        odor_sequences = pynwb.epoch.TimeIntervals(
            name="trials",
            description="The on/off timing of presented odors IDs.",
        )
        odor_sequences.add_column(name="odorant_id", description="The odorant ID that was presented during this trial.")
        odor_sequences.add_column(
            name="odorant",
            description=(
                "The chemical description of the odorant. "
                "According to one human (co-experimenter Kyoko Leaman) who smelled each substance smells like...\n"
                "Cinnamaldehyde: cinnamon\n"
                "Ethyl butyrate: pineapple, or similar to 2-Heptanone\n"
                "1-octanol: waxy\n"
                "Isobutyric acid: sour butter\n"
                "Benzaldehyde: bitter, like almond\n"
                "alpha-pinene: pine\n"
                "Isovaleric acid: stink or cheesy\n"
                "2-Heptanone: banana, or similar to Ethyl butyrate\n"
                "Propyl acetate: plum\n"
                "4-Methylvaleric acid: stinky"
            ),
        )
        odor_sequences.add_column(
            name="concentration", description="The concentration (in percent per volume) of the odorant."
        )

        odorant_id_to_chemical = dict()
        odorant_id_to_concentration = dict()
        for odor_id in odor_ids:
            if odor_id == "neutral":
                odorant_id_to_concentration[odor_id] = numpy.nan
                odorant_id_to_chemical[odor_id] = "mineral oil"
                continue

            odorant_key = f"odor{odor_id}"
            odorant_details = self.experiment_keys.get(odorant_key, None)

            if odorant_details is None:
                concentration = numpy.nan
                chemical = "Localizer"
            else:
                odorant_split = odorant_details.split(" ")

                match odorant_split[0]:
                    case "2-Heptanone":
                        concentration = "0.0004"  # From https://github.com/con/vandermeerlab-to-bids/issues/53
                        chemical = odorant_details
                    case _:
                        concentration = float(odorant_split[0].removesuffix("%")) / 100
                        chemical = " ".join(odorant_split[1:])

            odorant_id_to_concentration[odor_id] = concentration
            odorant_id_to_chemical[odor_id] = chemical

        all_trials = []
        for odor_id in odor_ids:
            channel_key = f"odor{odor_id}_channel" if odor_id != "neutral" else "neutral_odor_channel"
            channel_name = self.experiment_keys[channel_key]

            on_channel_file_path = self.preprocessed_data_directory / f"{channel_name}_ON.txt"
            off_channel_file_path = self.preprocessed_data_directory / f"{channel_name}_OFF.txt"

            with on_channel_file_path.open("r") as on_file_stream, off_channel_file_path.open("r") as off_file_stream:
                all_trials.extend(
                    [
                        {"start_time": float(on_time), "stop_time": float(off_time), "odorant_id": odor_id}
                        for on_time, off_time in zip(on_file_stream, off_file_stream)
                    ]
                )

        all_trials.sort(key=lambda row: row["start_time"])
        for row in all_trials:
            odor_sequences.add_row(
                start_time=row["start_time"],
                stop_time=row["stop_time"],
                odorant_id=row["odorant_id"],
                odorant=odorant_id_to_chemical[row["odorant_id"]],
                concentration=odorant_id_to_concentration[row["odorant_id"]],
            )
        nwbfile.trials = odor_sequences

        # Blocks (epochs)
        block_ids = self._get_block_ids()

        blocks = pynwb.epoch.TimeIntervals(
            name="epochs",
            description=(
                "Each block in this experiment involves a repetition of a subset of odor IDs, "
                "though the order of presentation may be randomized. 'UE' indicates the randomized "
                "'unpredictable environment' while 'SE' indicates the deterministic 'structured environment'."
            ),
        )
        blocks.add_column(name="block_id", description="The block ID that was presented during this epoch.")
        blocks.add_column(name="block_details", description="Details about which odorants were used per block.")

        experiment_notes = self.experiment_keys["notes"]
        if experiment_notes[:5] != "Block":
            message = "Experiment notes do not start with 'Block' - please adjust logic for extracting block details."
            raise NotImplementedError(message)

        notes_block_split = experiment_notes.split(", ")
        if len(notes_block_split) != len(block_ids):
            message = (
                "The number of blocks in the notes does not match the number of block IDs extracted - "
                "please adjust logic for extracting block details."
            )
            raise NotImplementedError(message)

        block_id_to_details = dict()
        for block_id, block_notes in zip(block_ids, notes_block_split):
            block_split = block_notes.split(":")
            details = block_split[1]
            block_id_to_details[block_id] = details

        all_epochs = []
        for block_id in block_ids:
            block_start_key = f"block{block_id}start"
            block_end_key = f"block{block_id}end"

            start_time = self.experiment_keys[block_start_key]
            stop_time = self.experiment_keys[block_end_key]
            all_epochs.append({"start_time": start_time, "stop_time": stop_time, "block_id": block_id})

        all_epochs.sort(key=lambda row: row["start_time"])
        for row in all_epochs:
            blocks.add_row(
                start_time=row["start_time"],
                stop_time=row["stop_time"],
                block_id=row["block_id"],
                block_details=block_id_to_details[row["block_id"]],
            )
        nwbfile.epochs = blocks

    def _get_odor_ids(self) -> list[str]:
        """Rather than hard-coding the odor types, we will extract them from the experiment keys."""
        pattern = r"odor([A-Z])_channel"

        matches = [
            result.group(1)
            for key in self.experiment_keys.keys()
            if (result := re.match(pattern=pattern, string=key)) is not None
        ]
        matches.append("neutral")
        return matches

    def _get_block_ids(self) -> list[str]:
        """Extract block IDs from the experiment keys."""
        pattern = r"block(\d+)_type"

        matches = [
            result.group(1)
            for key in self.experiment_keys.keys()
            if (result := re.match(pattern=pattern, string=key)) is not None
        ]
        return matches
