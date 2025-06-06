"""Rate limiting service.

This module provides rate limiting functionality using Redis.
"""

from datetime import datetime
import json
from typing import Tuple, Optional
import redis
from fastapi import HTTPException, Request
from services.common.config import Settings

class RateLimiter:
    """Redis-based rate limiter implementation."""

    def __init__(self, redis_url: str = "redis://localhost:6379/0"):
        """Initialize the rate limiter.
        
        Args:
            redis_url: Redis connection URL
        """
        self.redis = redis.from_url(redis_url)
        self.settings = Settings()

    def _get_key(self, api_key: str, endpoint: str) -> str:
        """Generate Redis key for rate limiting.
        
        Args:
            api_key: API key
            endpoint: API endpoint
            
        Returns:
            Redis key string
        """
        return f"rate_limit:{api_key}:{endpoint}"

    async def is_rate_limited(
        self, 
        api_key: str, 
        endpoint: str,
        max_requests: int = None,
        window_seconds: int = None
    ) -> Tuple[bool, dict]:
        """Check if request should be rate limited.
        
        Args:
            api_key: API key making the request
            endpoint: API endpoint being accessed
            max_requests: Maximum requests allowed in window (optional)
            window_seconds: Time window in seconds (optional)
            
        Returns:
            Tuple of (is_limited, limit_info)
        """
        # Use provided values or defaults from settings
        max_requests = max_requests or self.settings.rate_limit_requests
        window_seconds = window_seconds or self.settings.rate_limit_period
        
        key = self._get_key(api_key, endpoint)
        current_time = datetime.utcnow().timestamp()
        window_start = current_time - window_seconds

        # Clean old requests
        self.redis.zremrangebyscore(key, 0, window_start)
        
        # Get current request count
        request_count = self.redis.zcard(key)
        
        # Check if limit exceeded
        is_limited = request_count >= max_requests
        
        if not is_limited:
            # Add current request
            self.redis.zadd(key, {str(current_time): current_time})
            # Set expiry on the key
            self.redis.expire(key, window_seconds)
        
        # Calculate reset time
        if request_count > 0:
            try:
                oldest_request = float(self.redis.zrange(key, 0, 0)[0])
                reset_time = oldest_request + window_seconds
            except (IndexError, ValueError):
                reset_time = current_time + window_seconds
        else:
            reset_time = current_time + window_seconds
            
        return is_limited, {
            "limit": max_requests,
            "remaining": max(0, max_requests - request_count),
            "reset": int(reset_time),
            "window_seconds": window_seconds
        }

    async def get_custom_limits(self, api_key: str) -> Optional[dict]:
        """Get custom rate limits for an API key if configured.
        
        Args:
            api_key: API key to check
            
        Returns:
            Dictionary with custom limits or None
        """
        key = f"custom_limits:{api_key}"
        try:
            limits = self.redis.get(key)
            if limits:
                return json.loads(limits)
            return None
        except (json.JSONDecodeError, TypeError):
            return None

    async def set_custom_limits(
        self, 
        api_key: str, 
        max_requests: int,
        window_seconds: int
    ) -> None:
        """Set custom rate limits for an API key.
        
        Args:
            api_key: API key to set limits for
            max_requests: Maximum requests allowed
            window_seconds: Time window in seconds
        """
        key = f"custom_limits:{api_key}"
        limits = {
            "max_requests": max_requests,
            "window_seconds": window_seconds
        }
        self.redis.set(key, json.dumps(limits)) 