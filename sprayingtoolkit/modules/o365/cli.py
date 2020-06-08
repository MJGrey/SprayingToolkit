import asyncio
import typer
import logging
from sprayingtoolkit.modules.o365.sprayers.msol import MSOLSpray
from sprayingtoolkit.utils.common import coro
from sprayingtoolkit.models import O365SprayMethods, O365ValidationMethods

log = logging.getLogger("atomizer")
cli = typer.Typer()


@cli.command()
@coro
async def recon(target: str):
    """
    Validates that target is using O365
    """


@cli.command()
@coro
async def spray(
    target: str,
    username: str,
    password: str,
    interval: str = typer.Option("1:00:00"),
    spray_method: O365SprayMethods = typer.Option(O365SprayMethods.msol),
):
    """
    Spray O365
    """

    log.debug("Ok!")
    sprayer = MSOLSpray(interval)
    await sprayer.start(username, password)
    await sprayer.shutdown()


@cli.command()
@coro
async def validate(
    target: str,
    username: str,
    password: str,
    validation_method: O365ValidationMethods = typer.Option(
        O365ValidationMethods.uhoh365
    ),
):
    """
    Validate O365 accounts using a number of techniques 
    """

    log.debug("Ok!")
