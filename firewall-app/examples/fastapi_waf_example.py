"""
FastAPI WAF Integration Example

This example shows how to protect a FastAPI application with VESSA WAF.
"""

from fastapi import FastAPI, Depends
from fastapi.responses import JSONResponse
from services.waf import WAFMiddleware, WAFConfig
from services.waf.waf_config import BlockingMode

# Create FastAPI app
app = FastAPI(title="My Protected API")

# Configure WAF
waf_config = WAFConfig(
    mode=BlockingMode.BLOCK,
    enabled=True,
    log_blocked_requests=True
)

# Add WAF middleware
# This protects ALL routes automatically
app.add_middleware(WAFMiddleware, config=waf_config)


# Your routes - now protected by WAF!
@app.get("/")
async def root():
    """Public endpoint."""
    return {"message": "Hello, World!"}


@app.get("/api/data")
async def get_data():
    """API endpoint - automatically protected."""
    return {
        "data": [1, 2, 3, 4, 5],
        "status": "success"
    }


@app.post("/api/login")
async def login(username: str, password: str):
    """Login endpoint - protected against injection attacks."""
    # WAF will analyze this request before it reaches here
    # SQL injection attempts like: username="admin' OR '1'='1"
    # will be blocked automatically
    
    # Your login logic here
    return {"token": "abc123"}


@app.get("/api/user/{user_id}")
async def get_user(user_id: int):
    """User endpoint - protected against path traversal."""
    # Attempts like: /api/user/../../etc/passwd
    # will be blocked automatically
    
    return {"user_id": user_id, "name": "John Doe"}


# Health check endpoint (excluded from WAF in config)
@app.get("/health")
async def health():
    """Health check - bypasses WAF."""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

