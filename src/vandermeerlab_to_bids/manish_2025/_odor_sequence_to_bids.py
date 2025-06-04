"""Main code definition for the conversion of a full session (including NeuroPAL)."""

import datetime
import warnings
import typing

import yaml
import dateutil.tz
import pydantic

from ._manish_2025_converter import Manish2025Converter


@pydantic.validate_call
def odor_sequence_to_bids(
    *,
    data_directory: pydantic.DirectoryPath,
    subject_id: str,
    bids_directory: pydantic.DirectoryPath,
    raw_or_processed: typing.Literal["raw", "processed"],
    testing: bool = False,
    skip_existing: bool = True,
) -> None:
    # TODO
    pass
