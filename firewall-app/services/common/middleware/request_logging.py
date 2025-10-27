"""Request Logging Middleware.

This middleware logs all API requests with timing and context information.
"""

import time
import uuid
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from services.common.logging import get_logger


logger = get_logger(__name__)


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware to log all API requests."""
    
    def __init__(self, app: ASGIApp):
        """Initialize the middleware.
        
        Args:
            app: ASGI application
        """
        super().__init__(app)
    
    async def dispatch(self, request: Request, call_next):
        """Process the request and log it.
        
        Args:
            request: Incoming request
            call_next: Next middleware/handler
            
        Returns:
            Response from handler
        """
        # Generate request ID
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id
        
        # Get request details
        method = request.method
        path = request.url.path
        ip_address = request.client.host if request.client else "unknown"
        user_agent = request.headers.get("user-agent", "unknown")
        
        # Start timer
        start_time = time.time()
        
        # Log request start
        logger.debug(
            f"Request started: {method} {path}",
            request_id=request_id,
            method=method,
            path=path,
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        # Process request
        try:
            response = await call_next(request)
            
            # Calculate duration
            duration_ms = (time.time() - start_time) * 1000
            
            # Log API request
            logger.log_api_request(
                method=method,
                path=path,
                status_code=response.status_code,
                duration_ms=duration_ms,
                ip_address=ip_address,
                request_id=request_id,
                user_agent=user_agent
            )
            
            # Add request ID to response headers
            response.headers["X-Request-ID"] = request_id
            
            return response
            
        except Exception as e:
            # Calculate duration even on error
            duration_ms = (time.time() - start_time) * 1000
            
            # Log error
            logger.error(
                f"Request failed: {method} {path}",
                request_id=request_id,
                method=method,
                path=path,
                ip_address=ip_address,
                duration_ms=duration_ms,
                error=str(e),
                error_type=type(e).__name__
            )
            
            # Re-raise the exception
            raise

