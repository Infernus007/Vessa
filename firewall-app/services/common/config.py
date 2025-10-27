"""Common configuration module.

This module provides configuration settings for the VESSA Platform.
"""

import os
import sys
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator

class Settings(BaseSettings):
    """Application settings."""
    
    # Database - Required in production
    db_user: str
    db_password: str
    db_host: str = "localhost"
    db_port: str = "3306"
    db_name: str = "vessa"
    database_url: str | None = None
    
    # Security - REQUIRED, no defaults
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    @field_validator('secret_key')
    @classmethod
    def validate_secret_key(cls, v: str) -> str:
        """Validate that secret key is properly set."""
        if not v or v == "your-secret-key-here" or v == "CHANGE_ME" or len(v) < 32:
            error_msg = (
                "CRITICAL SECURITY ERROR: JWT secret_key must be set to a secure random string of at least 32 characters. "
                "Generate one with: openssl rand -hex 32"
            )
            print(f"\n{'='*80}\n{error_msg}\n{'='*80}\n", file=sys.stderr)
            raise ValueError(error_msg)
        return v
    
    # API
    api_v1_prefix: str = "/api/v1"
    
    # CORS
    cors_origins: list = ["*"]
    cors_methods: list = ["*"]
    cors_headers: list = ["*"]
    
    # Security headers
    security_headers: bool = True
    
    # Rate limiting
    rate_limit: bool = True
    rate_limit_requests: int = 100
    rate_limit_period: int = 60  # seconds
    
    # Server
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = True
    environment: str = "development"
    
    @field_validator('database_url')
    @classmethod
    def build_database_url(cls, v: str | None, info) -> str:
        """Build database URL from components if not provided."""
        if v:
            return v
        # Build from components
        values = info.data
        return f"mysql+pymysql://{values['db_user']}:{values['db_password']}@{values['db_host']}:{values['db_port']}/{values['db_name']}"
    
    @field_validator('environment')
    @classmethod
    def validate_environment(cls, v: str) -> str:
        """Validate environment setting."""
        allowed = ['development', 'staging', 'production']
        if v not in allowed:
            raise ValueError(f"environment must be one of {allowed}, got: {v}")
        return v
    
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,
        extra="allow"
    )

@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    try:
        settings = Settings()
        
        # Additional validation for production
        if settings.environment == "production":
            if settings.debug:
                print("\n⚠️  WARNING: Debug mode is enabled in production!\n", file=sys.stderr)
            if settings.cors_origins == ["*"]:
                raise ValueError("CORS wildcard origins are not allowed in production!")
        
        return settings
    except Exception as e:
        print(f"\n{'='*80}\nFATAL: Configuration error: {str(e)}\n{'='*80}\n", file=sys.stderr)
        sys.exit(1) 