from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
import logging
from exceptions import TourismBaseException

logger = logging.getLogger(__name__)

def register_error_handlers(app):
    @app.exception_handler(HTTPException)
    async def handle_http_exception(request: Request, e: HTTPException):
        logger.error(f"HTTP Error {e.status_code}: {e.detail}")
        return JSONResponse(
            status_code=e.status_code,
            content={
                "type": "about:blank",
                "title": "HTTP Error",
                "status": e.status_code,
                "detail": e.detail,
                "instance": str(request.url)
            }
        )

    @app.exception_handler(TourismBaseException)
    async def handle_custom_exception(request: Request, e: TourismBaseException):
        logger.error(f"Custom exception {e.status_code}: {e.message}")

        return JSONResponse(
            status_code=e.status_code,
            content={
                "type": "about:blank",
                "title": e.__class__.__name__,
                "status": e.status_code,
                "detail": e.message,
                "instance": str(request.url)
            }
        )

    @app.exception_handler(Exception)
    def handle_unexpected_error(request: Request, e: Exception):
        logger.error(f"Unexpected error: {str(e)}", exc_info=True)

        return JSONResponse(
            status_code=500,
            content={
                "type": "about:blank",
                "title": "Internal Server Error",
                "status": 500,
                "detail": "An unexpected error occurred",
                "instance": str(request.url)
            }
        )