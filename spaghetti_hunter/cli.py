import logging
import textwrap
from pathlib import Path
from typing import Optional

import typer
from typing_extensions import Annotated

from spaghetti_hunter import __app_name__
from spaghetti_hunter import __version__
from spaghetti_hunter.config import Settings
from spaghetti_hunter.config import setup_logging

setup_logging()
setings = Settings()
log = logging.getLogger(__name__)

app = typer.Typer(
    name=__app_name__,
    add_completion=False,
    rich_markup_mode='rich',
    no_args_is_help=True,
)


def version_callback(value: bool):
    if value:
        typer.echo(
            f'{__app_name__}: {typer.style(__version__, fg=typer.colors.YELLOW, bold=True)}'
        )
        raise typer.Exit()


@app.callback(
    epilog=textwrap.dedent("""\
    [blue]Note[/blue]: some monsters may still pass undetected, be aware           
    """)
)
def main(
        version: Annotated[
            Optional[bool],
            typer.Option(
                '--version',
                help='Show version information.',
                callback=version_callback,
                is_eager=True,
            ),
        ] = None,
):
    _ = version  # to not have unused argument


# reassign mains docstring manually, hack that allows f-string
main.__doc__ = f"""\b
[blue]
  _____                   _          _   _   _     _                 _
 / ____|                 | |        | | | | (_)   | |               | |
| (___  _ __   __ _  __ _| |__   ___| |_| |_ _    | |__  _   _ _ __ | |_ ___ _ __
 \___ \| '_ \ / _` |/ _` | '_ \ / _ \ __| __| |   | '_ \| | | | '_ \| __/ _ \ '__|
 ____) | |_) | (_| | (_| | | | |  __/ |_| |_| |   | | | | |_| | | | | ||  __/ |
|_____/| .__/ \__,_|\__, |_| |_|\___|\__|\__|_|   |_| |_|\__,_|_| |_|\__\___|_|
       | |           __/ |
       |_|          |___/[/blue]          [yellow]v{__version__}[/yellow]

Detect failed prints using ML and image classification.
"""


@app.command()
def classify(
        image: Annotated[
            Path,
            typer.Argument(
                exists=True,
                file_okay=True,
                dir_okay=False,
                resolve_path=True,
            )]
):
    """Detect failures in provided image."""
    log.info(f'got file: {image}')
    # TODO: run the classification


@app.command()
def sort(
        folder: Annotated[
            Path,
            typer.Argument(
                exists=True,
                file_okay=False,
                dir_okay=True,
                writable=False,
                readable=True,
                resolve_path=True,
            )]
):
    """Detect failures in provided image."""
    log.info(f'got folder: {folder}')
    # TODO: run the classification


if __name__ == '__main__':
    raise SystemExit(app())
