#!/usr/bin/env python3

import logging
import typer
import asyncio
import uvicorn
from sprayingtoolkit.api import atomizer
from sprayingtoolkit.modules import owa, lync, o365

handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter("[%(name)s] %(levelname)s - %(message)s"))
log = logging.getLogger("atomizer")
log.setLevel(logging.DEBUG)
log.addHandler(handler)

app = typer.Typer(context_settings={"show_default": True})
app.add_typer(o365.cli, name='o365', help='O365 pwnage')
app.add_typer(owa.cli, name='owa', help='OWA pwnage')
app.add_typer(lync.cli, name='lync', help='Lync/S4B pwnage')

@app.command(context_settings={"show_default": True})
def api(host: str = typer.Option("127.0.0.1", help="API interface"), port: int = typer.Option(8000, help="API port")):
    """
    Run the Atomizer API
    """

    log.info("Starting Atomizer api...")
    uvicorn.run(atomizer.api, host=host, port=port)

@app.callback()
def main(ctx: typer.Context, webhook: str = typer.Option(None, help="Webhook to use")):
    """
    Atomizer
    """

if __name__ == '__main__':
    app()
