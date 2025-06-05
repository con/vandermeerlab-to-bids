import pathlib
import pydantic
class BaseValidator:
    """
    Base class for validators in the van der Meer Lab to BIDS conversion process.

    This class provides a common interface and basic functionality for all validators.
    """

    @pydantic.validate_call
    def __init__(self, *, directory: str | pathlib.Path):
        self.directory = directory

        self.home_directory = pathlib.Path.home() / ".vandermeerlab_to_bids"
        self.home_directory.mkdir(exist_ok=True)

        self.records_directory = self.home_directory / "records"
        self.records_directory.mkdir(exist_ok=True)

