"""WAF Middleware for FastAPI and ASGI applications.

This module provides middleware that can be dropped into any ASGI application
to provide inline WAF protection.
"""

import asyncio
import time
from typing import Callable, Optional, Dict, Any
from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
import logging

from .waf_engine import WAFEngine
from .waf_config import WAFConfig, WAFAction

logger = logging.getLogger(__name__)


class WAFMiddleware(BaseHTTPMiddleware):
    """FastAPI/ASGI middleware for inline WAF protection.
    
    This middleware intercepts all requests and applies WAF analysis
    before they reach your application.
    
    Example:
        ```python
        from fastapi import FastAPI
        from services.waf import WAFMiddleware, WAFConfig
        
        app = FastAPI()
        
        # Add WAF middleware
        waf_config = WAFConfig()
        app.add_middleware(WAFMiddleware, config=waf_config)
        ```
    """
    
    def __init__(
        self,
        app: ASGIApp,
        config: Optional[WAFConfig] = None,
        db_session_factory: Optional[Callable] = None
    ):
        """Initialize WAF middleware.
        
        Args:
            app: ASGI application
            config: WAF configuration
            db_session_factory: Factory function to create DB sessions
        """
        super().__init__(app)
        self.config = config or WAFConfig()
        self.db_session_factory = db_session_factory
        
        # Create WAF engine
        db_session = db_session_factory() if db_session_factory else None
        self.waf_engine = WAFEngine(config=self.config, db_session=db_session)
        
        logger.info(f"WAF Middleware initialized in {self.config.mode} mode")
    
    async def dispatch(self, request: Request, call_next):
        """Process request through WAF.
        
        Args:
            request: Incoming request
            call_next: Next middleware/handler
            
        Returns:
            Response (blocked or from application)
        """
        # Skip if WAF is disabled
        if not self.config.enabled:
            return await call_next(request)
        
        # Extract request data
        method = request.method
        path = request.url.path
        headers = dict(request.headers)
        query_params = dict(request.query_params)
        client_ip = self._get_client_ip(request)
        
        # Get body (if present)
        body = None
        if method in ["POST", "PUT", "PATCH"]:
            try:
                # Read body once and cache it
                body_bytes = await request.body()
                if body_bytes:
                    content_type = headers.get("content-type", "")
                    if "application/json" in content_type:
                        import json
                        body = json.loads(body_bytes.decode())
                    elif "application/x-www-form-urlencoded" in content_type:
                        from urllib.parse import parse_qs
                        body = parse_qs(body_bytes.decode())
                    else:
                        body = body_bytes.decode()
                
                # Re-attach body to request for downstream handlers
                async def receive():
                    return {"type": "http.request", "body": body_bytes}
                request._receive = receive
            except Exception as e:
                logger.error(f"Failed to read request body: {str(e)}")
        
        # Analyze request
        start_time = time.time()
        try:
            decision = await self.waf_engine.analyze_request(
                method=method,
                path=path,
                headers=headers,
                body=body,
                query_params=query_params,
                client_ip=client_ip
            )
        except Exception as e:
            logger.error(f"WAF analysis failed: {str(e)}")
            # On error, allow request (fail open) but log it
            decision = None
        
        analysis_time = (time.time() - start_time) * 1000
        
        # Log decision
        if decision and self.config.log_blocked_requests and decision.should_block:
            logger.warning(
                f"WAF BLOCKED: {method} {path} from {client_ip} - "
                f"Score: {decision.threat_score:.2f}, Type: {decision.threat_type}, "
                f"Analysis: {analysis_time:.2f}ms"
            )
        
        if decision and self.config.log_allowed_requests and not decision.should_block:
            logger.info(
                f"WAF ALLOWED: {method} {path} from {client_ip} - "
                f"Score: {decision.threat_score:.2f}, Analysis: {analysis_time:.2f}ms"
            )
        
        # Take action based on decision
        if decision:
            if decision.action == WAFAction.BLOCK:
                # Block request
                return JSONResponse(
                    status_code=decision.response_code,
                    content=decision.response_body,
                    headers={
                        "X-WAF-Status": "blocked",
                        "X-WAF-Threat-Score": str(decision.threat_score),
                        "X-WAF-Threat-Type": decision.threat_type,
                        "X-WAF-Analysis-Time": f"{analysis_time:.2f}ms"
                    }
                )
            elif decision.action == WAFAction.CHALLENGE:
                # Return challenge response
                return JSONResponse(
                    status_code=decision.response_code,
                    content=decision.response_body,
                    headers={
                        "X-WAF-Status": "challenged",
                        "X-WAF-Threat-Score": str(decision.threat_score),
                        "X-WAF-Analysis-Time": f"{analysis_time:.2f}ms"
                    }
                )
        
        # Allow request to proceed
        response = await call_next(request)
        
        # Add WAF headers to response
        if decision:
            response.headers["X-WAF-Status"] = "allowed"
            response.headers["X-WAF-Threat-Score"] = str(decision.threat_score)
            response.headers["X-WAF-Analysis-Time"] = f"{analysis_time:.2f}ms"
        
        return response
    
    def _get_client_ip(self, request: Request) -> str:
        """Extract client IP from request.
        
        Handles proxy headers (X-Forwarded-For, X-Real-IP).
        
        Args:
            request: FastAPI request
            
        Returns:
            Client IP address
        """
        # Check for proxy headers
        forwarded_for = request.headers.get("x-forwarded-for")
        if forwarded_for:
            # Take first IP from comma-separated list
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("x-real-ip")
        if real_ip:
            return real_ip
        
        # Fall back to direct client
        if request.client:
            return request.client.host
        
        return "unknown"


def create_waf_middleware(
    config: Optional[WAFConfig] = None,
    db_session_factory: Optional[Callable] = None
) -> Callable:
    """Factory function to create WAF middleware.
    
    Args:
        config: WAF configuration
        db_session_factory: Factory to create DB sessions
        
    Returns:
        Middleware class configured with settings
    """
    def middleware_factory(app: ASGIApp) -> WAFMiddleware:
        return WAFMiddleware(
            app=app,
            config=config,
            db_session_factory=db_session_factory
        )
    
    return middleware_factory

