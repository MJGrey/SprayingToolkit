import asyncio
import typer
import logging
from sprayingtoolkit.utils.common import coro, beautify_json
from sprayingtoolkit.modules.lync.recon import LyncRecon
from sprayingtoolkit.modules.lync.sprayers import LyncSprayer

log = logging.getLogger("atomizer.modules.lync.cli")
cli = typer.Typer()


@cli.command(context_settings={"show_default": True})
@coro
async def spray(
    target: str,
    username: str, 
    password: str,
    interval: str = typer.Option("1:00:00"),
    interval_jitter: str = typer.Option("0:00:00"),
    auth_jitter: int = typer.Option(0)
):
    """
    Spray Lync/S4B
    """
    lync_recon = LyncRecon(target)
    try:
        recon_data = await lync_recon.start()
    finally:
        await lync_recon.shutdown()

    sprayer = LyncSprayer(**recon_data)
    sprayer.interval = interval
    sprayer.interval_jitter = interval_jitter
    sprayer.auth_jitter = auth_jitter
    try:
        results = await sprayer.start(username, password)
    finally:
        await sprayer.shutdown()


@cli.command()
@coro
async def recon(target: str,):
    """
    Perform recon only
    """

    lync_recon = LyncRecon(target)
    try:
        recon_data = await lync_recon.start()
    finally:
        await lync_recon.shutdown()

    log.info(beautify_json(recon_data))

