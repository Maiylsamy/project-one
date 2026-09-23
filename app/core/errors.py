# app/core/errors.py
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import logging

# Standard Python logging — writes errors to server logs (you can see them)
# but client never sees these details
logger = logging.getLogger(__name__)

def register_error_handlers(app: FastAPI):

    @app.exception_handler(Exception)
    # ↑ Catches EVERY unhandled exception across the whole app
    # This is your safety net — nothing slips through with raw error shown
    async def generic_error_handler(request: Request, exc: Exception):
        # Log the REAL error internally — you need this for debugging
        logger.error(f"Unhandled error: {exc}", exc_info=True)
        # exc_info=True → logs full traceback to your terminal/logs

        # But client gets ONLY this generic message — nothing revealing
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal server error"}
        )