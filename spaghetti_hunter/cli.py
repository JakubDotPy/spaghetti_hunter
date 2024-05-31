import logging
import textwrap
from pathlib import Path
from typing import Optional

import typer
from PIL import Image
from typing_extensions import Annotated

from spaghetti_hunter import __app_name__
from spaghetti_hunter import __version__
from spaghetti_hunter.config import settings
from spaghetti_hunter.config import setup_logging
from spaghetti_hunter.model_utils import detect
from spaghetti_hunter.model_utils import display_results
from spaghetti_hunter.model_utils import load_model

setup_logging()
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
        ctx: typer.Context,
        version: Annotated[
            Optional[bool],
            typer.Option(
                '--version',
                help='Show version information.',
                callback=version_callback,
                is_eager=True,
            ),
        ] = None,
        model_path: Annotated[
            Optional[Path],
            typer.Option(
                '--model', '-m',
                help='Load pretrained model from disk.',
            ),
        ] = settings.default_model,
):
    _ = version  # to not have unused argument
    model = load_model(model_path)
    ctx.obj = model


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


@app.command(deprecated=True)
def train():
    """Train an image classification model.

    This is command is not yet implemented.
    Use pretrained model instead.
    """
    log.warning('train command not yet supported')


@app.command()
def classify(
        ctx: typer.Context,
        image_path: Annotated[
            Path,
            typer.Argument(
                exists=True,
                file_okay=True,
                dir_okay=False,
                resolve_path=True,
            )]
):
    """Detect failures in provided image."""
    log.info(f'got file: {image_path}')

    if image_path.suffix.lower() not in settings.supported_image_formats:
        raise typer.BadParameter('Image format not supported')

    model = ctx.obj
    input_image = Image.open(image_path)
    image, boxes = detect(model, input_image)
    display_results(image_path, image, boxes)


@app.command(
    deprecated=True  # TODO: implement and remote this guard
)
def sort(
        input_dir: Annotated[
            Path,
            typer.Argument(
                help='image directory to be sorted',
                exists=True,
                file_okay=False,
                dir_okay=True,
                writable=False,
                readable=True,
                resolve_path=True,
            )],
        output_dir: Annotated[
            Path,
            typer.Argument(
                help='output directory with sorted images, will be created if necessary',
                file_okay=False,
                dir_okay=True,
                writable=True,
                readable=True,
                resolve_path=True,
            )] = Path.cwd() / 'output'
):
    """Sort folder of images displaying print failures.

    Create two sub-folders "OK" and "NOK" respectively.
    """
    log.info(f'input : {input_dir}')
    log.info(f'output: {output_dir}')

    images = [
        img
        for img in input_dir.iterdir()
        if img.suffix.lower() in settings.supported_image_formats
    ]

    log.info(f'found {len(images)} supported images')

    # TODO: implement and remote this guard
    log.warning('Unfortunately, this command is not yet supported')
    raise typer.Exit()

    # TODO: define the processing pipeline
    process_image = lambda x: None

    # TODO: use multiprocessing (img processing is cpu-bound) to sort the images
    from concurrent.futures import ProcessPoolExecutor
    with ProcessPoolExecutor() as executor:
        futures = [
            executor.submit(process_image, image)
            for image in images
        ]

    processed_images = []
    for future in futures:
        processed_images.append(future.result())


if __name__ == '__main__':
    raise SystemExit(app())
