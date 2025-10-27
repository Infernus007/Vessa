"""Security Headers Middleware.

This module provides middleware to add security headers to all HTTP responses,
protecting against common web vulnerabilities.
"""

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
import os


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Middleware to add security headers to responses."""
    
    def __init__(self, app: ASGIApp):
        super().__init__(app)
        self.environment = os.getenv("ENVIRONMENT", "development")
        self.is_production = self.environment == "production"
    
    async def dispatch(self, request: Request, call_next):
        """Add security headers to the response."""
        response: Response = await call_next(request)
        
        # Content Security Policy - Strict policy for production
        if self.is_production:
            csp = (
                "default-src 'self'; "
                "script-src 'self'; "
                "style-src 'self' 'unsafe-inline'; "
                "img-src 'self' data: https:; "
                "font-src 'self' data:; "
                "connect-src 'self'; "
                "frame-ancestors 'none'; "
                "base-uri 'self'; "
                "form-action 'self'"
            )
        else:
            # More permissive for development
            csp = (
                "default-src 'self' 'unsafe-inline' 'unsafe-eval' http://localhost:* ws://localhost:*; "
                "connect-src 'self' http://localhost:* ws://localhost:*"
            )
        
        response.headers["Content-Security-Policy"] = csp
        
        # Prevent clickjacking attacks
        response.headers["X-Frame-Options"] = "DENY"
        
        # Prevent MIME type sniffing
        response.headers["X-Content-Type-Options"] = "nosniff"
        
        # Enable XSS protection (for older browsers)
        response.headers["X-XSS-Protection"] = "1; mode=block"
        
        # Referrer Policy - Don't leak referrer information
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        
        # Permissions Policy - Restrict browser features
        response.headers["Permissions-Policy"] = (
            "geolocation=(), "
            "microphone=(), "
            "camera=(), "
            "payment=(), "
            "usb=(), "
            "magnetometer=(), "
            "gyroscope=(), "
            "accelerometer=()"
        )
        
        # HTTP Strict Transport Security (HTTPS only)
        # Only enable in production with HTTPS
        if self.is_production and request.url.scheme == "https":
            # max-age=31536000 is 1 year
            response.headers["Strict-Transport-Security"] = (
                "max-age=31536000; includeSubDomains; preload"
            )
        
        # Remove server header to hide technology stack
        if "Server" in response.headers:
            del response.headers["Server"]
        
        # Remove X-Powered-By if present
        if "X-Powered-By" in response.headers:
            del response.headers["X-Powered-By"]
        
        # Add custom security header for API version
        response.headers["X-API-Version"] = "1.0.0"
        
        # Cache control for sensitive data
        if request.url.path.startswith("/api/v1/"):
            # Don't cache API responses
            response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, private"
            response.headers["Pragma"] = "no-cache"
            response.headers["Expires"] = "0"
        
        return response


def add_security_headers_middleware(app):
    """Add security headers middleware to the FastAPI application."""
    app.add_middleware(SecurityHeadersMiddleware)
    return app

