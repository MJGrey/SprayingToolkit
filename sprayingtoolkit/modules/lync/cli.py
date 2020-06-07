import asyncio
import typer
import logging
from sprayingtoolkit.utils.common import coro, beautify_json
from sprayingtoolkit.modules.lync.recon import LyncRecon

log = logging.getLogger("atomizer.modules.lync.cli")
cli = typer.Typer()

@cli.command()
@coro
async def spray(
    target: str,
    username: str,
    password: str
):
    """
    Spray Lync/S4B
    """

    log.debug("Ok!")

@cli.command()
@coro
async def recon(
    target: str,
):
    """
    Perform recon only
    """

    lync_recon = LyncRecon(target)
    try:
        recon_data = await lync_recon.start()
    finally:
        await lync_recon.shutdown()

    log.info(beautify_json(recon_data))
