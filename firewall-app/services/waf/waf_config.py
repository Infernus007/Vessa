"""WAF Configuration Management.

This module handles WAF configuration including rules, policies, and settings.
"""

from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field
from enum import Enum
import yaml
import os


class BlockingMode(str, Enum):
    """WAF blocking modes."""
    BLOCK = "block"  # Block malicious requests
    LOG = "log"      # Log only, don't block
    CHALLENGE = "challenge"  # Present CAPTCHA/challenge
    SIMULATE = "simulate"  # Dry-run mode


class WAFAction(str, Enum):
    """Actions to take on threats."""
    ALLOW = "allow"
    BLOCK = "block"
    LOG = "log"
    RATE_LIMIT = "rate_limit"
    CHALLENGE = "challenge"


class ThreatThresholds(BaseModel):
    """Threat score thresholds for different actions."""
    block: float = Field(default=0.75, ge=0.0, le=1.0)
    challenge: float = Field(default=0.5, ge=0.0, le=1.0)
    log: float = Field(default=0.25, ge=0.0, le=1.0)


class RateLimitConfig(BaseModel):
    """Rate limiting configuration."""
    enabled: bool = True
    requests_per_minute: int = 60
    requests_per_hour: int = 1000
    burst_size: int = 10


class IPListConfig(BaseModel):
    """IP whitelist/blacklist configuration."""
    whitelist: List[str] = Field(default_factory=list)
    blacklist: List[str] = Field(default_factory=list)
    geo_block_countries: List[str] = Field(default_factory=list)


class AnalysisConfig(BaseModel):
    """Analysis configuration."""
    static_enabled: bool = True
    ml_enabled: bool = True
    ml_async: bool = True  # Run ML analysis async for performance
    threat_intel_enabled: bool = True
    cache_enabled: bool = True
    cache_ttl: int = 300  # 5 minutes


class WAFConfig(BaseModel):
    """WAF configuration."""
    
    # Mode
    mode: BlockingMode = BlockingMode.BLOCK
    enabled: bool = True
    
    # Thresholds
    thresholds: ThreatThresholds = Field(default_factory=ThreatThresholds)
    
    # Analysis settings
    analysis: AnalysisConfig = Field(default_factory=AnalysisConfig)
    
    # Rate limiting
    rate_limit: RateLimitConfig = Field(default_factory=RateLimitConfig)
    
    # IP management
    ip_config: IPListConfig = Field(default_factory=IPListConfig)
    
    # Custom rules
    custom_rules: List[Dict[str, Any]] = Field(default_factory=list)
    
    # Excluded paths (bypass WAF)
    excluded_paths: List[str] = Field(default_factory=lambda: [
        "/health",
        "/metrics",
        "/api/v1/health"
    ])
    
    # Logging
    log_blocked_requests: bool = True
    log_allowed_requests: bool = False
    detailed_logging: bool = False
    
    @classmethod
    def from_file(cls, config_path: str) -> "WAFConfig":
        """Load configuration from YAML file.
        
        Args:
            config_path: Path to configuration file
            
        Returns:
            WAFConfig instance
        """
        if not os.path.exists(config_path):
            return cls()
        
        with open(config_path, 'r') as f:
            config_data = yaml.safe_load(f)
        
        return cls(**config_data)
    
    def to_file(self, config_path: str) -> None:
        """Save configuration to YAML file.
        
        Args:
            config_path: Path to save configuration
        """
        with open(config_path, 'w') as f:
            yaml.dump(self.model_dump(), f, default_flow_style=False)
    
    def is_path_excluded(self, path: str) -> bool:
        """Check if a path is excluded from WAF protection.
        
        Args:
            path: Request path
            
        Returns:
            True if path is excluded
        """
        for excluded in self.excluded_paths:
            if path.startswith(excluded):
                return True
        return False
    
    def get_action_for_score(self, threat_score: float) -> WAFAction:
        """Determine action based on threat score.
        
        Args:
            threat_score: Threat score (0-1)
            
        Returns:
            WAFAction to take
        """
        if threat_score >= self.thresholds.block:
            return WAFAction.BLOCK
        elif threat_score >= self.thresholds.challenge:
            return WAFAction.CHALLENGE
        elif threat_score >= self.thresholds.log:
            return WAFAction.LOG
        else:
            return WAFAction.ALLOW

