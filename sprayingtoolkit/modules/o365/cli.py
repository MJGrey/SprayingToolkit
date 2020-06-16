import asyncio
import typer
import logging
from sprayingtoolkit.modules.o365.sprayers.msol import MSOLSpray
from sprayingtoolkit.modules.o365.validators.uhoh import UhOh365
from sprayingtoolkit.modules.o365.recon import O365Recon
from sprayingtoolkit.utils.common import coro
from sprayingtoolkit.models import O365SprayMethods, O365ValidationMethods
from sprayingtoolkit.utils.common import beautify_json

log = logging.getLogger("atomizer.modules.o365.cli")
cli = typer.Typer()


@cli.command()
@coro
async def recon(target: str):
    """
    Check if target is hosted on O365
    """

    o365_recon = O365Recon(target)
    try:
        recon_data = await o365_recon.start()
    finally:
        await o365_recon.shutdown()

    log.info(beautify_json(recon_data))

@cli.command(context_settings={"show_default": True})
@coro
async def spray(
    target: str,
    username: str,
    password: str,
    interval: str = typer.Option("1:00:00", "--interval", "-i", help="Interval between sprays"),
    interval_jitter: str = typer.Option("0:00:00", "--interval-jitter", "-j", help="Random delay on each spray"),
    auth_jitter: int = typer.Option(0, "--auth-jitter", "-a", help="Random delay between auth attempts in seconds"),
    spray_method: O365SprayMethods = typer.Option(O365SprayMethods.msol, help="Spray technique"),
):
    """
    Spray O365
    """

    sprayer = MSOLSpray()
    sprayer.interval = interval
    sprayer.interval_jitter = interval_jitter
    sprayer.auth_jitter = auth_jitter
    try:
        results = await sprayer.start(username, password)
    finally:
        await sprayer.shutdown()

@cli.command()
@coro
async def validate(
    target: str,
    username: str,
    validation_method: O365ValidationMethods = typer.Option(
        O365ValidationMethods.uhoh365
    ),
):
    """
    Validate O365 accounts using a number of techniques 
    """

    validator = UhOh365(target)
    await validator.start(username)
    await validator.shutdown()
