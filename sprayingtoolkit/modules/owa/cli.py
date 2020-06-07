import asyncio
import typer
import logging
from sprayingtoolkit.utils.common import coro, beautify_json
from sprayingtoolkit.modules.owa.recon import OwaRecon
from sprayingtoolkit.modules.owa.sprayers.owa import OwaSprayer

log = logging.getLogger("atomizer.modules.owa.cli")
cli = typer.Typer()

@cli.command()
@coro
async def spray(
    target: str,
    username: str,
    password: str
):
    """
    Spray OWA
    """
    owa_recon = OwaRecon(target)
    try:
        await owa_recon.start()
    finally:
        await owa_recon.shutdown()

    #OwaSprayer(**owa_recon)
    log.debug("Ok!")

@cli.command()
@coro
async def recon(
    target: str
):
    """
    Perform recon only
    """

    owa_recon = OwaRecon(target)
    try:
        recon_data = await owa_recon.start()
    finally:
        await owa_recon.shutdown()

    log.info(beautify_json(recon_data))
