import os
import typer

from .data import read_event
from .services import MADeliveryTimeService


app = typer.Typer()


@app.command()
def main(
    input_file: str = typer.Option(
        None,
        "--input_file",
        "-i",
        help="Path of the input file to process.",
    ),
    window_size: int = typer.Option(
        10, "--window_size", "-w", help="Number of past minutes to consider."
    ),
):
    if input_file is None:
        raise typer.BadParameter("input file argument is mandatory")

    if not os.path.exists(input_file):
        raise typer.BadParameter(f"file {input_file} does not exist")

    if window_size <= 0:
        raise typer.BadParameter("window size must be a positive integer")

    input_source = read_event(input_file)
    moving_average_service = MADeliveryTimeService(input_source, window_size)
    moving_average_service.process_events()
