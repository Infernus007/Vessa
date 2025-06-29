"""Threat Intelligence API schemas.

This module defines Pydantic models for threat intelligence API requests and responses.
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, validator
from datetime import datetime
import re

class IPReputationRequest(BaseModel):
    """Request model for IP reputation check."""
    ip: str = Field(..., description="IP address to check")
    
    @validator('ip')
    def validate_ip(cls, v):
        """Validate IP address format."""
        try:
            import ipaddress
            ipaddress.ip_address(v)
            return v
        except ValueError:
            raise ValueError('Invalid IP address format')

class IPReputationResponse(BaseModel):
    """Response model for IP reputation check."""
    ip: str
    is_malicious: bool
    threat_score: int = Field(..., ge=0, le=100)
    categories: List[str] = []
    sources: List[str] = []
    last_seen: Optional[datetime] = None
    first_seen: Optional[datetime] = None
    confidence: float = Field(..., ge=0.0, le=1.0)
    error: Optional[str] = None

class DomainReputationRequest(BaseModel):
    """Request model for domain reputation check."""
    domain: str = Field(..., description="Domain to check")
    
    @validator('domain')
    def validate_domain(cls, v):
        """Validate domain format."""
        if not re.match(r'^[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?(\.[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?)*$', v):
            raise ValueError('Invalid domain format')
        return v

class DomainReputationResponse(BaseModel):
    """Response model for domain reputation check."""
    domain: str
    is_malicious: bool
    threat_score: int = Field(..., ge=0, le=100)
    categories: List[str] = []
    sources: List[str] = []
    registration_date: Optional[datetime] = None
    expiration_date: Optional[datetime] = None
    confidence: float = Field(..., ge=0.0, le=1.0)
    error: Optional[str] = None

class URLReputationRequest(BaseModel):
    """Request model for URL reputation check."""
    url: str = Field(..., description="URL to check")
    
    @validator('url')
    def validate_url(cls, v):
        """Validate URL format."""
        if not re.match(r'^https?://[^\s/$.?#].[^\s]*$', v):
            raise ValueError('Invalid URL format')
        return v

class URLReputationResponse(BaseModel):
    """Response model for URL reputation check."""
    url: str
    is_malicious: bool
    threat_score: int = Field(..., ge=0, le=100)
    categories: List[str] = []
    sources: List[str] = []
    confidence: float = Field(..., ge=0.0, le=1.0)
    error: Optional[str] = None

class YARAMatchRequest(BaseModel):
    """Request model for YARA rule matching."""
    content: str = Field(..., description="Content to analyze")

class YARAMatch(BaseModel):
    """Model for individual YARA rule match."""
    rule_name: str
    pattern: str
    matched_text: str

class YARAMatchResponse(BaseModel):
    """Response model for YARA rule matching."""
    matches: List[YARAMatch] = []
    total_matches: int = Field(..., ge=0)
    is_suspicious: bool

class ThreatAnalysisRequest(BaseModel):
    """Request model for comprehensive threat analysis."""
    ip: Optional[str] = Field(None, description="IP address to analyze")
    domain: Optional[str] = Field(None, description="Domain to analyze")
    url: Optional[str] = Field(None, description="URL to analyze")
    content: Optional[str] = Field(None, description="Content to analyze")
    
    @validator('ip')
    def validate_ip(cls, v):
        """Validate IP address format if provided."""
        if v is not None:
            try:
                import ipaddress
                ipaddress.ip_address(v)
            except ValueError:
                raise ValueError('Invalid IP address format')
        return v

class ThreatAnalysisResponse(BaseModel):
    """Response model for comprehensive threat analysis."""
    timestamp: str
    indicators: Dict[str, Any] = {}
    overall_threat_score: int = Field(..., ge=0, le=100)
    is_malicious: bool
    recommendations: List[str] = []
    confidence: float = Field(..., ge=0.0, le=1.0) 