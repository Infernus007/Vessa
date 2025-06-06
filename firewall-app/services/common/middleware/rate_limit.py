"""Rate limiting middleware.

This module provides FastAPI middleware for rate limiting requests.
"""

from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from services.common.rate_limit import RateLimiter
from services.common.config import Settings

class RateLimitMiddleware(BaseHTTPMiddleware):
    """Middleware for rate limiting requests."""

    def __init__(self, app):
        """Initialize the middleware.
        
        Args:
            app: The ASGI application
        """
        super().__init__(app)
        self.settings = Settings()
        self.limiter = RateLimiter()

    async def dispatch(self, request: Request, call_next):
        """Process the request through rate limiting.
        
        Args:
            request: FastAPI request
            call_next: Next middleware/handler
            
        Returns:
            Response
        """
        # Skip rate limiting if disabled
        if not self.settings.rate_limit:
            return await call_next(request)

        # Get API key from header
        api_key = request.headers.get("x-api-key")
        if not api_key:
            return await call_next(request)

        # Get endpoint path for rate limiting
        endpoint = request.url.path

        # Check for custom limits
        custom_limits = await self.limiter.get_custom_limits(api_key)
        max_requests = None
        window_seconds = None
        if custom_limits:
            max_requests = custom_limits.get("max_requests")
            window_seconds = custom_limits.get("window_seconds")

        # Check rate limit
        is_limited, limit_info = await self.limiter.is_rate_limited(
            api_key,
            endpoint,
            max_requests,
            window_seconds
        )

        # Add rate limit headers
        headers = {
            "X-RateLimit-Limit": str(limit_info["limit"]),
            "X-RateLimit-Remaining": str(limit_info["remaining"]),
            "X-RateLimit-Reset": str(limit_info["reset"]),
            "X-RateLimit-Window": str(limit_info["window_seconds"])
        }

        if is_limited:
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={
                    "detail": "Rate limit exceeded",
                    "limit_info": limit_info
                },
                headers=headers
            )

        # Process request
        response = await call_next(request)

        # Add rate limit headers to response
        for key, value in headers.items():
            response.headers[key] = value

        return response 