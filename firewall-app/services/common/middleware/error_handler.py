import logging
from fastapi import Request, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
import traceback

logger = logging.getLogger(__name__)

class GlobalErrorHandlerMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        try:
            return await call_next(request)
        except Exception as e:
            # Log the full stack trace for debugging
            logger.error(f"Unhandled exception: {str(e)}")
            logger.error(traceback.format_exc())
            
            # Return a generic error message to the client
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={
                    "detail": "Internal Server Error",
                    "message": "An unexpected error occurred. Please try again later."
                }
            )
