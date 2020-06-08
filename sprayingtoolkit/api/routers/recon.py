import logging
from typing import Union
from pydantic import HttpUrl
from sprayingtoolkit.models import LyncReconData, OwaReconData, O365ReconData
from sprayingtoolkit.modules import lync, owa, o365
from fastapi import APIRouter, Request

log = logging.getLogger("atomizer.api.recon")

router = APIRouter()


@router.get("/owa")
async def owa_recon(request: Request, target: Union[str, HttpUrl]) -> OwaReconData:
    r = owa.recon(target)
    try:
        recon_data = await r.start()
        return OwaReconData(**recon_data)
    finally:
        await r.shutdown()


@router.get("/lync")
async def lync_recon(request: Request, target: Union[str, HttpUrl]) -> LyncReconData:
    r = lync.recon(target)
    try:
        recon_data = await r.start()
        return LyncReconData(**recon_data)
    finally:
        await r.shutdown()


@router.get("/o365")
async def o365_recon(request: Request, target: str) -> O365ReconData:
    pass
