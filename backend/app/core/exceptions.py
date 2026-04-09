from typing import Any, Dict, Optional
from fastapi import Request, status
from fastapi.responses import JSONResponse
from app.core.logging import get_logger

logger = get_logger("app")

class AppException(Exception):
    """Base exception for all application-specific errors."""
    def __init__(
        self,
        message: str,
        status_code: int = status.HTTP_400_BAD_REQUEST,
        details: Optional[Any] = None
    ):
        self.message = message
        self.status_code = status_code
        self.details = details
        super().__init__(message)

async def app_exception_handler(request: Request, exc: AppException):
    """Handler for AppException."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "message": exc.message,
            "details": exc.details
        }
    )

async def http_exception_handler(request: Request, exc: Any):
    """Handler for standard FastAPI/Starlette HTTPException."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "message": exc.detail,
        }
    )

async def generic_exception_handler(request: Request, exc: Exception):
    """Catch-all for any unhandled exceptions."""
    logger.exception(f"Unhandled error: {str(exc)}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "success": False,
            "message": "An unexpected error occurred. Please try again later.",
        }
    )
