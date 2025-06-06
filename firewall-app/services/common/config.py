"""Common configuration module.

This module provides configuration settings for the VESSA Platform.
"""

import os
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    """Application settings."""
    
    # Database
    db_user: str = "root"
    db_password: str = ""
    db_host: str = "localhost"
    db_port: str = "3306"
    db_name: str = "vessa"
    database_url: str = "mysql+pymysql://root:root@localhost:3306/vessa"
    
    # Security
    secret_key: str = "your-secret-key-here"  # Change in production
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
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
    
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        env_prefix="VESSA_",
        extra="allow"
    )

@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings() 