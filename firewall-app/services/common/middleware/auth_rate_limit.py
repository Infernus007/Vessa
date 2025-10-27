"""Enhanced Rate Limiting for Authentication Endpoints.

This middleware provides stricter rate limiting specifically for authentication
endpoints to prevent brute force attacks.
"""

import time
from typing import Dict, Tuple
from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
from collections import defaultdict
from datetime import datetime, timedelta


class AuthRateLimitMiddleware(BaseHTTPMiddleware):
    """Middleware for strict rate limiting on auth endpoints."""
    
    # Rate limits (per IP address)
    MAX_LOGIN_ATTEMPTS_PER_MINUTE = 5
    MAX_LOGIN_ATTEMPTS_PER_HOUR = 20
    MAX_LOGIN_ATTEMPTS_PER_DAY = 50
    
    # Lockout duration after exceeding limits
    LOCKOUT_DURATION_MINUTES = 15
    
    # Track attempts: {ip: [(timestamp, endpoint), ...]}
    attempts: Dict[str, list] = defaultdict(list)
    
    # Track lockouts: {ip: lockout_until_timestamp}
    lockouts: Dict[str, float] = {}
    
    def __init__(self, app: ASGIApp):
        """Initialize the middleware.
        
        Args:
            app: ASGI application
        """
        super().__init__(app)
    
    async def dispatch(self, request: Request, call_next):
        """Process the request with auth rate limiting.
        
        Args:
            request: Incoming request
            call_next: Next middleware/handler
            
        Returns:
            Response from handler or rate limit error
        """
        # Only apply to auth endpoints
        if not self._is_auth_endpoint(request.url.path):
            return await call_next(request)
        
        # Get client IP
        ip_address = self._get_client_ip(request)
        
        # Check if IP is locked out
        if self._is_locked_out(ip_address):
            lockout_until = datetime.fromtimestamp(self.lockouts[ip_address])
            remaining = int((lockout_until - datetime.now()).total_seconds())
            
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Too many failed authentication attempts. Locked out for {remaining} seconds.",
                headers={
                    "Retry-After": str(remaining),
                    "X-RateLimit-Limit": str(self.MAX_LOGIN_ATTEMPTS_PER_MINUTE),
                    "X-RateLimit-Remaining": "0",
                    "X-RateLimit-Reset": str(int(self.lockouts[ip_address]))
                }
            )
        
        # Check rate limits
        self._check_rate_limits(ip_address, request.url.path)
        
        # Record attempt
        current_time = time.time()
        self.attempts[ip_address].append((current_time, request.url.path))
        
        # Clean old attempts (older than 24 hours)
        self._cleanup_old_attempts(ip_address)
        
        # Process request
        response = await call_next(request)
        
        # If login failed (401 or 403), keep the attempt recorded
        # If login succeeded (200), we could clear attempts for this IP
        if response.status_code == 200 and request.method == "POST":
            # Successful auth - clear attempts
            self.attempts[ip_address] = []
            if ip_address in self.lockouts:
                del self.lockouts[ip_address]
        
        # Add rate limit headers
        minute_count, hour_count, day_count = self._get_attempt_counts(ip_address)
        response.headers["X-RateLimit-Limit-Minute"] = str(self.MAX_LOGIN_ATTEMPTS_PER_MINUTE)
        response.headers["X-RateLimit-Remaining-Minute"] = str(max(0, self.MAX_LOGIN_ATTEMPTS_PER_MINUTE - minute_count))
        response.headers["X-RateLimit-Limit-Hour"] = str(self.MAX_LOGIN_ATTEMPTS_PER_HOUR)
        response.headers["X-RateLimit-Remaining-Hour"] = str(max(0, self.MAX_LOGIN_ATTEMPTS_PER_HOUR - hour_count))
        
        return response
    
    def _is_auth_endpoint(self, path: str) -> bool:
        """Check if path is an authentication endpoint.
        
        Args:
            path: Request path
            
        Returns:
            True if auth endpoint
        """
        auth_patterns = [
            "/api/v1/auth/token",
            "/api/v1/auth/register",
            "/api/v1/auth/refresh",
            "/api/v1/auth/reset-password",
        ]
        return any(pattern in path for pattern in auth_patterns)
    
    def _get_client_ip(self, request: Request) -> str:
        """Get client IP address from request.
        
        Args:
            request: Incoming request
            
        Returns:
            Client IP address
        """
        # Check X-Forwarded-For header (if behind proxy)
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            # Take first IP in the chain
            return forwarded_for.split(",")[0].strip()
        
        # Check X-Real-IP header
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip
        
        # Fall back to client.host
        if request.client:
            return request.client.host
        
        return "unknown"
    
    def _is_locked_out(self, ip_address: str) -> bool:
        """Check if IP is currently locked out.
        
        Args:
            ip_address: Client IP address
            
        Returns:
            True if locked out
        """
        if ip_address not in self.lockouts:
            return False
        
        # Check if lockout has expired
        if time.time() > self.lockouts[ip_address]:
            del self.lockouts[ip_address]
            return False
        
        return True
    
    def _check_rate_limits(self, ip_address: str, path: str) -> None:
        """Check if IP has exceeded rate limits.
        
        Args:
            ip_address: Client IP address
            path: Request path
            
        Raises:
            HTTPException: If rate limit exceeded
        """
        minute_count, hour_count, day_count = self._get_attempt_counts(ip_address)
        
        # Check per-minute limit
        if minute_count >= self.MAX_LOGIN_ATTEMPTS_PER_MINUTE:
            self._apply_lockout(ip_address)
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Rate limit exceeded: {minute_count} attempts in last minute. Maximum: {self.MAX_LOGIN_ATTEMPTS_PER_MINUTE}",
                headers={
                    "Retry-After": "60",
                    "X-RateLimit-Limit": str(self.MAX_LOGIN_ATTEMPTS_PER_MINUTE),
                    "X-RateLimit-Remaining": "0"
                }
            )
        
        # Check per-hour limit
        if hour_count >= self.MAX_LOGIN_ATTEMPTS_PER_HOUR:
            self._apply_lockout(ip_address)
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Rate limit exceeded: {hour_count} attempts in last hour. Maximum: {self.MAX_LOGIN_ATTEMPTS_PER_HOUR}",
                headers={
                    "Retry-After": "3600",
                    "X-RateLimit-Limit": str(self.MAX_LOGIN_ATTEMPTS_PER_HOUR),
                    "X-RateLimit-Remaining": "0"
                }
            )
        
        # Check per-day limit
        if day_count >= self.MAX_LOGIN_ATTEMPTS_PER_DAY:
            self._apply_lockout(ip_address)
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Rate limit exceeded: {day_count} attempts in last 24 hours. Maximum: {self.MAX_LOGIN_ATTEMPTS_PER_DAY}",
                headers={
                    "Retry-After": "86400",
                    "X-RateLimit-Limit": str(self.MAX_LOGIN_ATTEMPTS_PER_DAY),
                    "X-RateLimit-Remaining": "0"
                }
            )
    
    def _get_attempt_counts(self, ip_address: str) -> Tuple[int, int, int]:
        """Get attempt counts for different time windows.
        
        Args:
            ip_address: Client IP address
            
        Returns:
            Tuple of (minute_count, hour_count, day_count)
        """
        current_time = time.time()
        minute_ago = current_time - 60
        hour_ago = current_time - 3600
        day_ago = current_time - 86400
        
        attempts = self.attempts.get(ip_address, [])
        
        minute_count = sum(1 for timestamp, _ in attempts if timestamp > minute_ago)
        hour_count = sum(1 for timestamp, _ in attempts if timestamp > hour_ago)
        day_count = sum(1 for timestamp, _ in attempts if timestamp > day_ago)
        
        return minute_count, hour_count, day_count
    
    def _apply_lockout(self, ip_address: str) -> None:
        """Apply lockout to IP address.
        
        Args:
            ip_address: Client IP address
        """
        lockout_until = time.time() + (self.LOCKOUT_DURATION_MINUTES * 60)
        self.lockouts[ip_address] = lockout_until
        
        print(f"[AUTH_RATE_LIMIT] IP {ip_address} locked out until {datetime.fromtimestamp(lockout_until)}")
    
    def _cleanup_old_attempts(self, ip_address: str) -> None:
        """Remove attempts older than 24 hours.
        
        Args:
            ip_address: Client IP address
        """
        current_time = time.time()
        day_ago = current_time - 86400
        
        if ip_address in self.attempts:
            self.attempts[ip_address] = [
                (timestamp, path) for timestamp, path in self.attempts[ip_address]
                if timestamp > day_ago
            ]
            
            # Remove IP from tracking if no recent attempts
            if not self.attempts[ip_address]:
                del self.attempts[ip_address]

