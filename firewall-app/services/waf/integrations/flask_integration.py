"""Flask integration for VESSA WAF.

This module provides a decorator and middleware for protecting Flask applications.

Example:
    from flask import Flask
    from services.waf.integrations import FlaskWAF
    
    app = Flask(__name__)
    waf = FlaskWAF(app)
    
    @app.route('/')
    def index():
        return 'Hello, World!'
"""

from functools import wraps
from typing import Optional, Callable
import time
import logging

try:
    from flask import Flask, request, jsonify, abort
    FLASK_AVAILABLE = True
except ImportError:
    FLASK_AVAILABLE = False
    Flask = None

from ..waf_engine import WAFEngine
from ..waf_config import WAFConfig, WAFAction

logger = logging.getLogger(__name__)


class FlaskWAF:
    """Flask integration for VESSA WAF.
    
    This class provides Flask middleware that protects your application
    with minimal code changes.
    
    Example:
        ```python
        from flask import Flask
        from services.waf.integrations import FlaskWAF
        
        app = Flask(__name__)
        
        # Option 1: Protect entire app
        waf = FlaskWAF(app)
        
        # Option 2: Protect specific routes
        waf = FlaskWAF()
        
        @app.route('/api/data')
        @waf.protect
        def get_data():
            return {'data': 'value'}
        ```
    """
    
    def __init__(
        self,
        app: Optional[Flask] = None,
        config: Optional[WAFConfig] = None
    ):
        """Initialize Flask WAF integration.
        
        Args:
            app: Flask application (optional)
            config: WAF configuration
        """
        if not FLASK_AVAILABLE:
            raise ImportError("Flask is not installed. Install with: pip install flask")
        
        self.config = config or WAFConfig()
        self.waf_engine = WAFEngine(config=self.config)
        
        if app is not None:
            self.init_app(app)
    
    def init_app(self, app: Flask):
        """Initialize WAF with Flask app.
        
        This registers a before_request handler that protects all routes.
        
        Args:
            app: Flask application
        """
        @app.before_request
        def waf_before_request():
            """Check every request before it reaches the handler."""
            return self._check_request()
        
        logger.info(f"Flask WAF initialized in {self.config.mode} mode")
    
    def protect(self, func: Callable) -> Callable:
        """Decorator to protect individual Flask routes.
        
        Args:
            func: Route handler function
            
        Returns:
            Wrapped function with WAF protection
        """
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Check request
            block_response = self._check_request()
            if block_response:
                return block_response
            
            # Call original function
            return func(*args, **kwargs)
        
        return wrapper
    
    def _check_request(self):
        """Check current request against WAF.
        
        Returns:
            None if allowed, Response if blocked
        """
        if not self.config.enabled:
            return None
        
        # Get request data
        method = request.method
        path = request.path
        headers = dict(request.headers)
        query_params = dict(request.args)
        client_ip = self._get_client_ip()
        
        # Get body
        body = None
        if method in ["POST", "PUT", "PATCH"]:
            try:
                if request.is_json:
                    body = request.get_json()
                elif request.form:
                    body = dict(request.form)
                else:
                    body = request.get_data(as_text=True)
            except:
                pass
        
        # Run async analysis in sync context (Flask is sync)
        import asyncio
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
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
        
        # Log decision
        if decision.should_block:
            logger.warning(
                f"WAF BLOCKED: {method} {path} from {client_ip} - "
                f"Score: {decision.threat_score:.2f}, Type: {decision.threat_type}"
            )
        
        # Return block response if needed
        if decision.action == WAFAction.BLOCK:
            response = jsonify(decision.response_body)
            response.status_code = decision.response_code
            response.headers["X-WAF-Status"] = "blocked"
            response.headers["X-WAF-Threat-Score"] = str(decision.threat_score)
            response.headers["X-WAF-Threat-Type"] = decision.threat_type
            return response
        
        elif decision.action == WAFAction.CHALLENGE:
            response = jsonify(decision.response_body)
            response.status_code = decision.response_code
            response.headers["X-WAF-Status"] = "challenged"
            return response
        
        # Add WAF headers for allowed requests
        @request.after_this_request
        def add_waf_headers(response):
            response.headers["X-WAF-Status"] = "allowed"
            response.headers["X-WAF-Threat-Score"] = str(decision.threat_score)
            return response
        
        return None
    
    def _get_client_ip(self) -> str:
        """Get client IP from Flask request."""
        if request.headers.get("X-Forwarded-For"):
            return request.headers["X-Forwarded-For"].split(",")[0].strip()
        elif request.headers.get("X-Real-IP"):
            return request.headers["X-Real-IP"]
        else:
            return request.remote_addr or "unknown"
    
    def get_stats(self) -> dict:
        """Get WAF statistics.
        
        Returns:
            Statistics dictionary
        """
        return self.waf_engine.get_stats()


def protect_flask_route(
    config: Optional[WAFConfig] = None
) -> Callable:
    """Decorator factory for protecting Flask routes.
    
    This is a convenience function for protecting individual routes
    without initializing the full FlaskWAF class.
    
    Args:
        config: WAF configuration
        
    Returns:
        Decorator function
    
    Example:
        ```python
        from flask import Flask
        from services.waf.integrations import protect_flask_route
        
        app = Flask(__name__)
        
        @app.route('/api/data')
        @protect_flask_route()
        def get_data():
            return {'data': 'value'}
        ```
    """
    waf = FlaskWAF(config=config)
    return waf.protect

