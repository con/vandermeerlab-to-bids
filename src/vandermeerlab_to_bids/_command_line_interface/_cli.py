import typing
import pathlib
import click

from ..manish_2025._odor_sequence_to_nwb import odor_sequence_to_nwb


# vandermeerlab2bids
@click.group()
def _vandermeerlab_to_bids_cli():
    """Tools for managing data from the van der Meer Lab."""
    pass


# vandermeerlab2bids convert
@_vandermeerlab_to_bids_cli.group(name="convert")
def _vandermeerlab_to_bids_convert_cli():
    """Data conversion tools for van der Meer Lab."""
    pass


# vandermeerlab2bids convert nwb
@_vandermeerlab_to_bids_convert_cli.command(name="nwb")
@click.option(
    "--datapath", type=click.Path(writable=True), help="Path to the directory containing all the data the experiment."
)
@click.option(
    "--outpath",
    help="The directory in which to save the NWB files.",
    required=True,
    type=click.Path(writable=True),
)
@click.option(
    "--experiment",
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
    "--testing",
    help="Whether or not to 'test' the conversion process by limiting the amount of data written to the NWB files.",
    is_flag=True,  # Overrides the dtype to be boolean
    required=False,
    default=False,
)
def _vandermeerlab_to_bids_convert_nwb_cli(
    data_directory: str,
    outpath: str,
    experiment: typing.Literal["OdorSequence"],
    subject: str,
    session: str,
    testing: bool = False,
) -> None:
    """Convert the given experiment type to NWB format."""
    data_directory = pathlib.Path(data_directory)
    outpath = pathlib.Path(outpath)

    match experiment:
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
            message = f"Experiment type '{experiment}' is not yet supported."
            raise NotImplementedError(message)
