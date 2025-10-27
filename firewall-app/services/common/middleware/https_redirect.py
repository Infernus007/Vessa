"""HTTPS Redirect Middleware.

This middleware enforces HTTPS in production by redirecting all HTTP requests
to HTTPS.
"""

import os
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import RedirectResponse
from starlette.types import ASGIApp


class HTTPSRedirectMiddleware(BaseHTTPMiddleware):
    """Middleware to enforce HTTPS in production."""
    
    def __init__(self, app: ASGIApp):
        """Initialize the middleware.
        
        Args:
            app: ASGI application
        """
        super().__init__(app)
        
        # Only enforce in production
        self.enabled = os.getenv("ENVIRONMENT", "development") == "production"
        
        # Allow disabling via environment variable
        if os.getenv("HTTPS_REDIRECT", "true").lower() == "false":
            self.enabled = False
    
    async def dispatch(self, request: Request, call_next):
        """Process the request and enforce HTTPS if needed.
        
        Args:
            request: Incoming request
            call_next: Next middleware/handler
            
        Returns:
            Response from handler or redirect to HTTPS
        """
        # Skip if not enabled (development/staging)
        if not self.enabled:
            return await call_next(request)
        
        # Check if request is already HTTPS
        if self._is_https(request):
            # Add HSTS header
            response = await call_next(request)
            
            # Strict-Transport-Security header
            # Start with short duration, increase gradually in production
            # max-age=31536000 (1 year) after testing
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains; preload"
            
            return response
        
        # Redirect HTTP to HTTPS
        https_url = self._get_https_url(request)
        
        return RedirectResponse(
            url=https_url,
            status_code=301  # Permanent redirect
        )
    
    def _is_https(self, request: Request) -> bool:
        """Check if request is HTTPS.
        
        Args:
            request: Incoming request
            
        Returns:
            True if HTTPS
        """
        # Check URL scheme
        if request.url.scheme == "https":
            return True
        
        # Check X-Forwarded-Proto header (when behind reverse proxy)
        forwarded_proto = request.headers.get("X-Forwarded-Proto", "").lower()
        if forwarded_proto == "https":
            return True
        
        # Check X-Forwarded-SSL header
        forwarded_ssl = request.headers.get("X-Forwarded-SSL", "").lower()
        if forwarded_ssl == "on":
            return True
        
        return False
    
    def _get_https_url(self, request: Request) -> str:
        """Convert HTTP URL to HTTPS.
        
        Args:
            request: Incoming request
            
        Returns:
            HTTPS URL
        """
        # Get the original URL
        url = str(request.url)
        
        # Replace http:// with https://
        if url.startswith("http://"):
            return url.replace("http://", "https://", 1)
        
        # Already HTTPS (shouldn't happen, but just in case)
        return url

