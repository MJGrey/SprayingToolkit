import logging
import uvicorn
from fastapi import FastAPI, Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sprayingtoolkit.exceptions import AutodiscoverUrlNotFound, LyncBaseUrlNotFound
from sprayingtoolkit.api.routers import spray, recon, validate

log = logging.getLogger("atomizer.api")

api = FastAPI(title="Atomizer API")
#app.state.SCANS = ActiveScans()
api.include_router(spray.router, prefix="/spray", tags=["scan"])
api.include_router(recon.router, prefix="/recon", tags=["recon"])
api.include_router(validate.router, prefix="/validate", tags=["validate"])

@api.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=jsonable_encoder({"detail": exc.errors(), "body": exc.body}),
    )

@api.exception_handler(AutodiscoverUrlNotFound)
async def autodiscover_url_not_found_exception_handler(request: Request, exc: AutodiscoverUrlNotFound):
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"error": str(exc)},
    )

@api.exception_handler(LyncBaseUrlNotFound)
async def lync_base_url_not_found_exception_handler(request: Request, exc: LyncBaseUrlNotFound):
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"error": str(exc)},
    )

if __name__ == "__main__":
    uvicorn.run(api, host="127.0.0.1", port=8000)
