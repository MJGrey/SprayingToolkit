#!/usr/bin/env python3

import logging
import typer
import asyncio
import uvicorn
import webbrowser
from sprayingtoolkit.api import atomizer
from sprayingtoolkit.modules import owa, lync, o365

__version__ = "1.0.0"
__codename__ = "Young Terps"

handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter("[%(name)s] %(levelname)s - %(message)s"))
log = logging.getLogger("atomizer")
log.setLevel(logging.DEBUG)
log.addHandler(handler)

app = typer.Typer(
    context_settings={"show_default": True},
    epilog="Lemon banangie sour tangie, guava dawg terp wave, but some people call it gelato OG",
    short_help=True,
    no_args_is_help=True,
)

app.add_typer(o365.cli, name="o365", help="O365 pwnage")
app.add_typer(owa.cli, name="owa", help="OWA pwnage")
app.add_typer(lync.cli, name="lync", help="Lync/S4B pwnage")

def version_callback(value: bool):
    if value:
        typer.echo(f'{__version__} - "{__codename__}"')
        raise typer.Exit()

def turpanese_callback(value: bool):
    if value:
        webbrowser.open("https://www.youtube.com/embed/XOJAddj_SJE?autoplay=1", new=2)
        raise typer.Exit()

@app.command(context_settings={"show_default": True})
def api(
    host: str = typer.Option("127.0.0.1", help="API interface"),
    port: int = typer.Option(8000, help="API port"),
):
    """
    Run the Atomizer API
    """

    log.info("Starting Atomizer api...")
    uvicorn.run(atomizer.api, host=host, port=port)


@app.callback()
def main(
    ctx: typer.Context,
    webhook: str = typer.Option(None, help="Webhook to use"),
    version: bool = typer.Option(None, "--version", callback=version_callback, help="Show version and exit"),
    teach_me_turpanese: bool = typer.Option(None, "--teach-me-turpanese", callback=turpanese_callback, help="Learn to speak Turpanese")
):

    """
    Atomizer ⚛️
    """


if __name__ == "__main__":
    app()
