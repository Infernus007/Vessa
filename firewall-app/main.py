"""VESSA Platform API / WAF.

This module is the main entry point for the VESSA Platform.

Modes:
1. API Mode (default) - Security analysis and incident management API
2. WAF Mode (optional) - Inline Web Application Firewall protection

Before running the server, ensure you have:
1. Set up your database configuration in .env file
2. Run database migrations: python cli.py db init
3. Created an admin user: python cli.py user create --role admin

WAF Mode:
Set WAF_ENABLED=true in .env to enable inline WAF protection for this API.
Or use standalone reverse proxy mode: python -m services.waf.reverse_proxy
"""

import os
from dotenv import load_dotenv
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from typing import Dict, Any

from services.auth.api.routes import router as auth_router
from services.user.api.routes import router as user_router
from services.incident.api.routes import router as incident_router
from services.notification.api.routes import router as notification_router
from services.threat_intelligence.api.routes import router as threat_intelligence_router
from services.common.middleware.rate_limit import RateLimitMiddleware
from services.common.middleware.security_headers import SecurityHeadersMiddleware
from services.common.middleware.request_logging import RequestLoggingMiddleware
from services.common.middleware.auth_rate_limit import AuthRateLimitMiddleware
from services.common.middleware.https_redirect import HTTPSRedirectMiddleware
from services.common.database.session import get_db
from services.incident.core.incident_service import IncidentService
from services.incident.api.schemas import SimpleRequestAnalysis, ThreatAnalysisResponse
from services.common.utils.input_sanitizer import sanitize_for_ml_analysis

# Load environment variables
load_dotenv()

# WAF Integration (optional)
WAF_ENABLED = os.getenv("WAF_ENABLED", "false").lower() == "true"
if WAF_ENABLED:
    try:
        from services.waf import WAFMiddleware, WAFConfig
        from services.waf.waf_config import BlockingMode
        print("[INFO] WAF mode is ENABLED")
    except ImportError as e:
        print(f"[WARNING] WAF requested but dependencies missing: {e}")
        WAF_ENABLED = False

# Create FastAPI application
app = FastAPI(
    title="VESSA WAF & Security Platform" if WAF_ENABLED else "VESSA Platform API",
    description="ML-Powered Web Application Firewall and Security Analysis Platform" if WAF_ENABLED else "Security Incident Management and Analysis Platform",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure security
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")

# Configure CORS
origins = [
    "http://localhost:3000",
    "http://localhost:5173",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:5173",
    "http://localhost:8000",
    "ws://localhost:3000",
    "ws://localhost:5173",
    "ws://127.0.0.1:3000",
    "ws://127.0.0.1:5173",
    "ws://localhost:8000"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=3600,
)

# Add middlewares in order (last added = first executed)

# 0. WAF protection (if enabled) - FIRST LINE OF DEFENSE
if WAF_ENABLED:
    waf_config = WAFConfig(
        mode=BlockingMode(os.getenv("WAF_MODE", "block")),
        enabled=True,
        log_blocked_requests=True
    )
    app.add_middleware(
        WAFMiddleware,
        config=waf_config,
        db_session_factory=lambda: next(get_db())
    )
    print(f"[INFO] WAF protection active in {waf_config.mode} mode")

# 1. Request logging (logs all requests)
app.add_middleware(RequestLoggingMiddleware)

# 2. Auth rate limiting (strict limits for auth endpoints)
app.add_middleware(AuthRateLimitMiddleware)

# 3. Security headers (applied to all responses)
app.add_middleware(SecurityHeadersMiddleware)

# 4. HTTPS redirect (enforce HTTPS in production)
app.add_middleware(HTTPSRedirectMiddleware)

# 5. General rate limiting (blocks excessive requests)
app.add_middleware(RateLimitMiddleware)

# Include routers with API versioning
app.include_router(auth_router, prefix="/api/v1/auth")
app.include_router(user_router, prefix="/api/v1/users")
app.include_router(incident_router, prefix="/api/v1/incidents")
app.include_router(notification_router, prefix="/api/v1/notifications")
app.include_router(threat_intelligence_router, prefix="/api/v1/threat-intelligence")

# Global health endpoint as documented
@app.get("/api/v1/health", tags=["Health"])
async def health_check():
    """Health check endpoint with model status."""
    try:
        # Check if absolution package is available
        try:
            from absolution.model_loader import ModelLoader
            model_status = "loaded"
        except ImportError:
            model_status = "unavailable"
        
        return {
            "status": "healthy",
            "version": "1.0.0",
            "model_status": model_status
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "version": "1.0.0",
            "model_status": "error",
            "error": str(e)
        }

# Main analyze endpoint as documented
@app.post("/api/v1/analyze", response_model=ThreatAnalysisResponse, tags=["Analysis"])
async def analyze_request(
    request: SimpleRequestAnalysis,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Analyze a request for security threats.
    
    This endpoint provides the main request analysis functionality as documented.
    All inputs are sanitized before analysis to prevent injection attacks.
    """
    try:
        # Sanitize inputs before processing (prevents XXE, injection attacks)
        sanitized_data = sanitize_for_ml_analysis(
            client_ip=request.client_ip,
            request_path=request.request_path,
            request_method=request.request_method,
            request_headers=request.request_headers,
            request_body=request.request_body
        )
        
        service = IncidentService(db)
        
        # Extract user agent from sanitized headers
        user_agent = sanitized_data["request_headers"].get("User-Agent", "")
        
        # Perform analysis with sanitized data
        analysis_result = await service.analyze_request(
            source_ip=sanitized_data["client_ip"],
            request_path=sanitized_data["request_path"],
            request_method=sanitized_data["request_method"],
            headers=sanitized_data["request_headers"],
            body=sanitized_data["request_body"],
            user_agent=user_agent
        )
        
        return ThreatAnalysisResponse(
            threat_score=analysis_result.get("threat_score", 0.0),
            threat_type=analysis_result.get("threat_type", "unknown"),
            findings=analysis_result.get("findings", []),
            should_block=analysis_result.get("should_block", False)
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Analysis failed: {str(e)}"
        )

@app.get("/", tags=["Root"])
async def root():
    """Root endpoint providing API information."""
    return {
        "message": "Welcome to VESSA Platform API",
        "version": "1.0.0",
        "docs_url": "/docs",
        "api_version": "v1",
        "endpoints": {
            "health": "/api/v1/health",
            "analyze": "/api/v1/analyze",
            "docs": "/docs"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=os.getenv("HOST", "0.0.0.0"),
        port=int(os.getenv("PORT", "8000")),
        reload=bool(os.getenv("DEBUG", "True")),
        workers=1,  # Single worker for development
        reload_excludes=["*.pyc", "*.pyo", "*.pyd", "*.so"],  # Exclude binary files from reload
        server_header=False,  # Don't expose server version
        proxy_headers=True  # Trust proxy headers
    )