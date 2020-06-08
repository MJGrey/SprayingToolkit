import asyncio
import logging
from typing import Union
from pydantic import HttpUrl
from sprayingtoolkit.modules import lync, owa, o365
from sprayingtoolkit.models import SprayParams
from fastapi import APIRouter, Request

log = logging.getLogger("atomizer.api.spray")

router = APIRouter()


@router.post("/owa")
async def owa_spray(
    request: Request, target: Union[str, HttpUrl], spray_params: SprayParams
):
    pass


@router.post("/lync")
async def lync_spray(
    request: Request, target: Union[str, HttpUrl], spray_params: SprayParams
):
    pass


@router.post("/o365")
async def o365_spray(
    request: Request, target: Union[str, HttpUrl], spray_params: SprayParams
):
    pass
