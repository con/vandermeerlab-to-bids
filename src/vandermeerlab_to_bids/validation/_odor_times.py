from ._base_validator import BaseValidator
import numpy
from ..utils import read_experiment_keys_file

class OdorTimesValidator(BaseValidator):
    """
    Validator for odor times in the source data.

    Ensures the oddness of 'matching' does not need to be done post-hoc during conversion, as from
    https://github.com/vandermeerlab/mvdmlab_npx_to_nwb/blob/15c85df2803293f8de331caf34980d9f239727bc/src/manimoh_nwb_converters/odorseq_convert_behavior.py#L45
    """

    def __init__(self, directory: str):
        super().__init__(directory=directory)

        self.experiment_keys_file_paths = list(directory.rglob("*_keys.m"))

    def validate(self, expected_delay: float = 2.0, tolerance: float = 0.25) -> None:
        """Validate the odor times in the source data."""
        for experiment_key_file_path in self.experiment_keys_file_paths:
            subject_id, year, month, day, _ = experiment_key_file_path.stem.split("_")

            experiment_keys = read_experiment_keys_file(file_path=experiment_key_file_path)

            odor_channels = {key: channel for key, channel in experiment_keys.items() if key.startswith("odor") and key.endswith("_channel")}

            for key, channel in odor_channels.items():
                on_file_path = experiment_key_file_path.parent / f"{channel}_ON.txt"
                off_file_path = experiment_key_file_path.parent / f"{channel}_OFF.txt"

                on_content = numpy.array(object=[float(value) for value in on_file_path.read_text().splitlines()])
                off_content = numpy.array(object=[float(value) for value in off_file_path.read_text().splitlines()])

                if on_content.size != off_content.size:
                    message = ValueError(
                        f"Mismatch in number of ON and OFF times for {key} in {experiment_key_file_path.stem}: "
                        f"{on_content.size} ON times, {off_content.size} OFF times."
                    )
                    raise ValueError(message)

                difference = off_content - on_content

                if not numpy.allclose(a=difference, b=expected_delay, atol=tolerance):
                    message = ValueError(
                        f"ON and OFF times for {key} in {experiment_key_file_path.stem} do not match expected delay of "
                        f"{expected_delay}s with a tolerance of {tolerance}s."
                    )
                    raise ValueError(message)
