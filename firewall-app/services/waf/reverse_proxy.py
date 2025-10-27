"""Reverse Proxy WAF - Standalone mode.

This module provides a standalone reverse proxy WAF that sits in front
of your application without requiring code changes.

Usage:
    python -m services.waf.reverse_proxy --backend http://localhost:3000 --port 8080
"""

import asyncio
import argparse
import logging
from typing import Optional
import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import Response
import httpx

from .waf_engine import WAFEngine
from .waf_config import WAFConfig, WAFAction

logger = logging.getLogger(__name__)


class ReverseProxyWAF:
    """Standalone reverse proxy WAF.
    
    This sits in front of your application and protects it without
    requiring any code changes to your app.
    
    Architecture:
        Client → ReverseProxyWAF (analyze & filter) → Your Application
    """
    
    def __init__(
        self,
        backend_url: str,
        config: Optional[WAFConfig] = None,
        host: str = "0.0.0.0",
        port: int = 8080
    ):
        """Initialize reverse proxy WAF.
        
        Args:
            backend_url: URL of backend application (e.g., http://localhost:3000)
            config: WAF configuration
            host: Host to bind to
            port: Port to listen on
        """
        self.backend_url = backend_url.rstrip("/")
        self.config = config or WAFConfig()
        self.host = host
        self.port = port
        
        # Create FastAPI app
        self.app = FastAPI(title="VESSA Reverse Proxy WAF")
        
        # Create WAF engine
        self.waf_engine = WAFEngine(config=self.config)
        
        # HTTP client for proxying requests
        self.client = httpx.AsyncClient(
            timeout=30.0,
            follow_redirects=True
        )
        
        # Register routes
        self._setup_routes()
        
        logger.info(
            f"Reverse Proxy WAF initialized: "
            f"{self.host}:{self.port} -> {self.backend_url}"
        )
    
    def _setup_routes(self):
        """Set up proxy routes."""
        
        @self.app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS", "HEAD"])
        async def proxy_handler(request: Request, path: str):
            """Handle all requests and proxy to backend."""
            return await self._handle_request(request, path)
        
        @self.app.get("/waf/stats")
        async def waf_stats():
            """Get WAF statistics."""
            return self.waf_engine.get_stats()
        
        @self.app.get("/waf/health")
        async def waf_health():
            """WAF health check."""
            return {
                "status": "healthy",
                "mode": self.config.mode,
                "backend": self.backend_url
            }
    
    async def _handle_request(self, request: Request, path: str) -> Response:
        """Handle incoming request.
        
        Args:
            request: FastAPI request
            path: Request path
            
        Returns:
            Response (blocked or proxied)
        """
        # Extract request data
        method = request.method
        headers = dict(request.headers)
        query_params = dict(request.query_params)
        client_ip = self._get_client_ip(request)
        
        # Get body
        body = None
        if method in ["POST", "PUT", "PATCH"]:
            body_bytes = await request.body()
            if body_bytes:
                try:
                    body = body_bytes.decode()
                except:
                    body = body_bytes
        
        # Analyze request
        decision = await self.waf_engine.analyze_request(
            method=method,
            path=f"/{path}",
            headers=headers,
            body=body,
            query_params=query_params,
            client_ip=client_ip
        )
        
        # Block if necessary
        if decision.should_block:
            logger.warning(
                f"WAF BLOCKED: {method} /{path} from {client_ip} - "
                f"Score: {decision.threat_score:.2f}, Type: {decision.threat_type}"
            )
            
            return Response(
                content=str(decision.response_body),
                status_code=decision.response_code,
                headers={
                    "X-WAF-Status": "blocked",
                    "X-WAF-Threat-Score": str(decision.threat_score),
                    "X-WAF-Threat-Type": decision.threat_type,
                    "Content-Type": "application/json"
                }
            )
        
        # Proxy request to backend
        try:
            backend_url = f"{self.backend_url}/{path}"
            if query_params:
                query_str = "&".join([f"{k}={v}" for k, v in query_params.items()])
                backend_url += f"?{query_str}"
            
            # Remove hop-by-hop headers
            proxy_headers = {
                k: v for k, v in headers.items()
                if k.lower() not in [
                    "host", "connection", "keep-alive", "proxy-authenticate",
                    "proxy-authorization", "te", "trailers", "transfer-encoding", "upgrade"
                ]
            }
            
            # Add X-Forwarded headers
            proxy_headers["X-Forwarded-For"] = client_ip
            proxy_headers["X-Forwarded-Proto"] = request.url.scheme
            proxy_headers["X-WAF-Protected"] = "true"
            proxy_headers["X-WAF-Threat-Score"] = str(decision.threat_score)
            
            # Make request to backend
            if method == "GET":
                response = await self.client.get(backend_url, headers=proxy_headers)
            elif method == "POST":
                response = await self.client.post(backend_url, content=body_bytes if body else None, headers=proxy_headers)
            elif method == "PUT":
                response = await self.client.put(backend_url, content=body_bytes if body else None, headers=proxy_headers)
            elif method == "DELETE":
                response = await self.client.delete(backend_url, headers=proxy_headers)
            elif method == "PATCH":
                response = await self.client.patch(backend_url, content=body_bytes if body else None, headers=proxy_headers)
            elif method == "OPTIONS":
                response = await self.client.options(backend_url, headers=proxy_headers)
            elif method == "HEAD":
                response = await self.client.head(backend_url, headers=proxy_headers)
            else:
                return Response(content="Method not allowed", status_code=405)
            
            # Return backend response
            response_headers = dict(response.headers)
            response_headers["X-WAF-Status"] = "allowed"
            
            return Response(
                content=response.content,
                status_code=response.status_code,
                headers=response_headers
            )
            
        except httpx.RequestError as e:
            logger.error(f"Failed to proxy request to backend: {str(e)}")
            return Response(
                content=f"Bad Gateway: Failed to connect to backend",
                status_code=502
            )
    
    def _get_client_ip(self, request: Request) -> str:
        """Extract client IP from request."""
        forwarded_for = request.headers.get("x-forwarded-for")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("x-real-ip")
        if real_ip:
            return real_ip
        
        if request.client:
            return request.client.host
        
        return "unknown"
    
    def run(self):
        """Run the reverse proxy WAF."""
        logger.info(f"Starting Reverse Proxy WAF on {self.host}:{self.port}")
        logger.info(f"Proxying to: {self.backend_url}")
        logger.info(f"WAF Mode: {self.config.mode}")
        
        uvicorn.run(
            self.app,
            host=self.host,
            port=self.port,
            log_level="info"
        )


def main():
    """CLI entry point for reverse proxy WAF."""
    parser = argparse.ArgumentParser(description="VESSA Reverse Proxy WAF")
    parser.add_argument(
        "--backend",
        required=True,
        help="Backend URL (e.g., http://localhost:3000)"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8080,
        help="Port to listen on (default: 8080)"
    )
    parser.add_argument(
        "--host",
        default="0.0.0.0",
        help="Host to bind to (default: 0.0.0.0)"
    )
    parser.add_argument(
        "--config",
        help="Path to WAF configuration file (YAML)"
    )
    parser.add_argument(
        "--mode",
        choices=["block", "log", "challenge", "simulate"],
        default="block",
        help="WAF mode (default: block)"
    )
    
    args = parser.parse_args()
    
    # Load config
    if args.config:
        config = WAFConfig.from_file(args.config)
    else:
        config = WAFConfig()
    
    # Override mode if specified
    if args.mode:
        from .waf_config import BlockingMode
        config.mode = BlockingMode(args.mode)
    
    # Create and run proxy
    proxy = ReverseProxyWAF(
        backend_url=args.backend,
        config=config,
        host=args.host,
        port=args.port
    )
    
    proxy.run()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()

