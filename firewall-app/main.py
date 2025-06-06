"""VESSA Platform API.

This module is the main entry point for the VESSA Platform API.
Before running the server, ensure you have:
1. Set up your database configuration in .env file
2. Run database migrations: python cli.py db init
3. Created an admin user: python cli.py user create --role admin
"""

import os
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer

from services.auth.api.routes import router as auth_router
from services.user.api.routes import router as user_router
from services.incident.api.routes import router as incident_router
from services.notification.api.routes import router as notification_router
from services.common.middleware.rate_limit import RateLimitMiddleware

# Load environment variables
load_dotenv()

# Create FastAPI application
app = FastAPI(
    title="VESSA Platform API",
    description="Security Incident Management and Analysis Platform",
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

# Add rate limiting middleware
app.add_middleware(RateLimitMiddleware)

# Include routers
app.include_router(auth_router, prefix="/auth")
app.include_router(user_router, prefix="/users")
app.include_router(incident_router, prefix="/incidents")
app.include_router(notification_router, prefix="/notifications")

@app.get("/", tags=["Root"])
async def root():
    """Root endpoint providing API information."""
    return {
        "message": "Welcome to VESSA Platform API",
        "version": "1.0.0",
        "docs_url": "/docs"
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