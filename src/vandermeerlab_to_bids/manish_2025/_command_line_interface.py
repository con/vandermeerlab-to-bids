"""Command line interface wrapper around the PumpProbe conversion function."""

import pathlib

import click
import pydantic

from ._odor_sequence_to_bids import odor_sequence_to_bids


# vandermeerlab2bids
@click.group()
def _vandermeerlab2bids_cli():
    pass


@_vandermeerlab2bids_cli.command(name="odorseq")
@click.option(
    "--data_directory",
    help="""
The base directory containing experiment data.

Expected to be structured similar to...

|- OdorSequence
|--- sourcedata
|----- preprocessed
|------- < subject ID >
|--------- < subject ID >-< session ID >
|----- raw
|------- < subject ID >
|--------- < subject ID >-< session ID >_< SpikeGLX gate >

For example...

|- OdorSequence
|--- sourcedata
|----- preprocessed
|------- M541
|--------- M541-2024-08-31
|----- raw
|------- M541
|--------- M541-2024-08-31_g0
""",
    required=True,
    type=click.Path(writable=False),
)
@click.option(
    "--subject_id",
    help="ID of the subject.",
    required=True,
    type=str,
)
@click.option(
    "--session_id",
    help="ID of the subject.",
    required=True,
    type=str,
)
@click.option(
    "--bids_directory",
    help="The folder path to save the BIDS-organized NWB files to.",
    required=True,
    type=click.Path(writable=True),
)
@click.option(
    "--testing",
    help="""
Whether or not to 'test' the conversion process by limiting the amount of data written to the BIDS-organized NWB files.

Note that files produced in this way will not save in the `bids_directory`, but rather in a folder adjacent to
it marked as `bids_testing`.
""",
    is_flag=True,  # This overrides the dtype to be boolean
    required=False,
    default=False,
)
def _odor_sequence_to_bids_cli(
    *,
    data_directory: pydantic.DirectoryPath,
    subject_id: str,
    session_id: str,
    bids_directory: pydantic.DirectoryPath,
    testing: bool = False,
) -> None:
    bids_directory = pathlib.Path(bids_directory)

    odor_sequence_to_bids(
        data_directory=data_directory,
        subject_id=subject_id,
        session_id=session_id,
        bids_directory=bids_directory,
        testing=testing,
    )
