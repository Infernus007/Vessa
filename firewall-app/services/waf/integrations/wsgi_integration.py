"""WSGI middleware integration for VESSA WAF.

This provides WSGI middleware that can be used with any WSGI-compliant
application (Flask, Django, Pyramid, etc.).
"""

import asyncio
from typing import Dict, Any, Optional, Callable
import logging

from ..waf_engine import WAFEngine
from ..waf_config import WAFConfig, WAFAction

logger = logging.getLogger(__name__)


class WSGIWAFMiddleware:
    """WSGI middleware for VESSA WAF.
    
    This can be used with any WSGI application.
    
    Example:
        ```python
        from flask import Flask
        from services.waf.integrations import WSGIWAFMiddleware
        
        app = Flask(__name__)
        app.wsgi_app = WSGIWAFMiddleware(app.wsgi_app)
        ```
    """
    
    def __init__(
        self,
        app: Callable,
        config: Optional[WAFConfig] = None
    ):
        """Initialize WSGI WAF middleware.
        
        Args:
            app: WSGI application
            config: WAF configuration
        """
        self.app = app
        self.config = config or WAFConfig()
        self.waf_engine = WAFEngine(config=self.config)
        
        logger.info(f"WSGI WAF initialized in {self.config.mode} mode")
    
    def __call__(self, environ: Dict[str, Any], start_response: Callable):
        """Handle WSGI request.
        
        Args:
            environ: WSGI environment
            start_response: WSGI start_response callable
            
        Returns:
            Response iterable
        """
        if not self.config.enabled:
            return self.app(environ, start_response)
        
        # Extract request data
        method = environ.get("REQUEST_METHOD", "GET")
        path = environ.get("PATH_INFO", "/")
        query_string = environ.get("QUERY_STRING", "")
        client_ip = self._get_client_ip(environ)
        
        # Build headers dict
        headers = {}
        for key, value in environ.items():
            if key.startswith("HTTP_"):
                header_name = key[5:].replace("_", "-").lower()
                headers[header_name] = value
        
        # Parse query params
        query_params = {}
        if query_string:
            for param in query_string.split("&"):
                if "=" in param:
                    key, value = param.split("=", 1)
                    query_params[key] = value
        
        # Get body
        body = None
        if method in ["POST", "PUT", "PATCH"]:
            try:
                content_length = int(environ.get("CONTENT_LENGTH", 0))
                if content_length > 0:
                    body = environ["wsgi.input"].read(content_length)
                    # Reset input stream for downstream app
                    from io import BytesIO
                    environ["wsgi.input"] = BytesIO(body)
                    body = body.decode("utf-8")
            except:
                pass
        
        # Run WAF analysis
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            decision = loop.run_until_complete(
                self.waf_engine.analyze_request(
                    method=method,
                    path=path,
                    headers=headers,
                    body=body,
                    query_params=query_params,
                    client_ip=client_ip
                )
            )
        finally:
            loop.close()
        
        # Block if necessary
        if decision.should_block:
            logger.warning(
                f"WAF BLOCKED: {method} {path} from {client_ip} - "
                f"Score: {decision.threat_score:.2f}, Type: {decision.threat_type}"
            )
            
            # Return block response
            import json
            response_body = json.dumps(decision.response_body).encode("utf-8")
            response_headers = [
                ("Content-Type", "application/json"),
                ("Content-Length", str(len(response_body))),
                ("X-WAF-Status", "blocked"),
                ("X-WAF-Threat-Score", str(decision.threat_score)),
                ("X-WAF-Threat-Type", decision.threat_type)
            ]
            
            start_response(
                f"{decision.response_code} Forbidden",
                response_headers
            )
            return [response_body]
        
        # Modify start_response to add WAF headers
        def waf_start_response(status, response_headers, exc_info=None):
            response_headers.append(("X-WAF-Status", "allowed"))
            response_headers.append(("X-WAF-Threat-Score", str(decision.threat_score)))
            return start_response(status, response_headers, exc_info)
        
        # Call wrapped app
        return self.app(environ, waf_start_response)
    
    def _get_client_ip(self, environ: Dict[str, Any]) -> str:
        """Extract client IP from WSGI environment."""
        # Check for proxy headers
        forwarded_for = environ.get("HTTP_X_FORWARDED_FOR")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        real_ip = environ.get("HTTP_X_REAL_IP")
        if real_ip:
            return real_ip
        
        return environ.get("REMOTE_ADDR", "unknown")

