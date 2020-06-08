import logging
from sprayingtoolkit.models import ValidateParams
from fastapi import APIRouter, Request

log = logging.getLogger("atomizer.api.validate")

router = APIRouter()


@router.post("/o365")
async def validate(request: Request, validate_params: ValidateParams):
    pass
