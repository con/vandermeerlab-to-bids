import typing
import pathlib
import click

from ..manish_2025._odor_sequence_to_nwb import odor_sequence_to_nwb


# vandermeerlab2bids
@click.group()
def _vandermeerlab_to_bids_cli():
    pass


# vandermeerlab2bids convert
@click.group(name="convert")
def _vandermeerlab_to_bids_convert_cli():
    pass


# vandermeerlab2bids convert nwb
@_vandermeerlab_to_bids_convert_cli.command(name="nwb")
@click.argument("data_directory", type=click.Path(writable=True))
@click.option(
    "experiment_type",
    type=click.Choice(["OdorSequence"], case_sensitive=False),
    help="The specifier of the experiment to convert (e.g., 'OdorSequence').",
)
@click.option(
    "--subject",
    help="ID of the subject.",
    required=True,
    type=str,
)
@click.option(
    "--session",
    help="ID of the subject.",
    required=True,
    type=str,
)
@click.option(
    "--outpath",
    help="The directory in which to save the NWB files.",
    required=True,
    type=click.Path(writable=True),
)
@click.option(
    "--testing",
    help="Whether or not to 'test' the conversion process by limiting the amount of data written to the NWB files.",
    is_flag=True,  # This overrides the dtype to be boolean
    required=False,
    default=False,
)
def _vandermeerlab_to_bids_convert_nwb_cli(
    data_directory: str,
    experiment_type: typing.Literal["OdorSequence"],
    subject: str,
    session: str,
    outpath: pathlib.Path,
    testing: bool = False,
) -> None:
    """
        Convert the given experiment type to NWB format.

        SESSION_DIRECTORY: Path to the directory containing all the data the experiment.

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
    """
    data_directory = pathlib.Path(data_directory)

    match experiment_type:
        case "OdorSequence":
            odor_sequence_to_nwb(
                data_directory=data_directory,
                subject_id=subject,
                session_id=session,
                nwb_directory=outpath,
                testing=testing,
                raw_or_processed="both",
            )
        case _:
            message = f"Experiment type '{experiment_type}' is not yet supported."
            raise NotImplementedError(message)
