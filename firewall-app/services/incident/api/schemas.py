"""Incident API schemas.

This module defines Pydantic models for request/response validation in the incident API.
"""

from datetime import datetime
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field, field_validator
from enum import Enum

class RequestMethod(str, Enum):
    """Valid HTTP request methods."""
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"
    PATCH = "PATCH"
    HEAD = "HEAD"
    OPTIONS = "OPTIONS"

class ThreatType(str, Enum):
    """Types of security threats."""
    SQL_INJECTION = "sql_injection"
    XSS = "xss"
    COMMAND_INJECTION = "command_injection"
    PATH_TRAVERSAL = "path_traversal"
    NOSQL_INJECTION = "nosql_injection"
    SAFE = "safe"
    SUSPICIOUS = "suspicious"
    BENIGN = "benign"
    DESERIALIZATION = "deserialization"
    GRAPHQL_ATTACKS = "graphql_attacks"
    JWT_ATTACKS = "jwt_attacks"
    LFI = "lfi"
    MODERN_CMDI = "modern_cmdi"
    MODERN_FILE_ATTACKS = "modern_file_attacks"
    MODERN_SQLI = "modern_sqli"
    MODERN_SSRF = "modern_ssrf"
    MODERN_XSS = "modern_xss"
    OPEN_REDIRECT = "open_redirect"
    PROTOTYPE_POLLUTION = "prototype_pollution"
    SQLI = "sqli"
    SSRF = "ssrf"
    TEMPLATE_INJECTION = "template_injection"
    XXE_INJECTION = "xxe_injection"

class IncidentSeverity(str, Enum):
    """Incident severity levels."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

class IncidentStatus(str, Enum):
    """Incident status values."""
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    CLOSED = "closed"

class ResponsePriority(str, Enum):
    """Response priority levels."""
    IMMEDIATE = "immediate"
    HIGH = "high"
    NORMAL = "normal"
    LOW = "low"

class MaliciousRequestCreate(BaseModel):
    """Schema for creating a malicious request record."""
    request_method: RequestMethod
    request_url: str = Field(..., max_length=2048)
    request_path: str = Field(..., max_length=1024)
    request_headers: Dict[str, str]
    request_query_params: Optional[Dict[str, str]] = None
    request_body: Optional[Dict[str, Any]] = None
    client_ip: str = Field(..., max_length=45)  # IPv6 max length
    timestamp: datetime
    service_name: str = Field(..., max_length=255)
    service_version: Optional[str] = Field(None, max_length=50)

class RawRequestAnalysis(BaseModel):
    """Schema for analyzing raw request data from middleware."""
    method: str
    url: str
    path: str
    headers: Dict[str, str]
    query_params: Optional[Dict[str, str]] = None
    body: Optional[Any] = None
    client_ip: str
    timestamp: Optional[datetime] = None

class ThreatAnalysisResponse(BaseModel):
    """Schema for threat analysis response."""
    threat_score: float = Field(..., ge=0.0, le=1.0)
    threat_type: ThreatType
    findings: List[str]
    should_block: bool

class IncidentCreate(BaseModel):
    """Schema for creating an incident."""
    title: str = Field(..., max_length=255)
    description: str = Field(..., max_length=2048)
    severity: IncidentSeverity
    affected_assets: Optional[List[str]] = None
    tags: Optional[List[str]] = None
    detection_source: str = Field(..., max_length=50)
    reporter_id: Optional[str] = None

class IncidentUpdate(BaseModel):
    """Schema for updating an incident."""
    title: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = Field(None, max_length=2048)
    severity: Optional[IncidentSeverity] = None
    status: Optional[IncidentStatus] = None
    resolution_notes: Optional[str] = Field(None, max_length=2048)
    mitigation_steps: Optional[List[str]] = None
    false_positive: Optional[bool] = None

class IncidentResponse(BaseModel):
    """Schema for incident response."""
    id: str
    title: str
    description: str
    severity: IncidentSeverity
    status: IncidentStatus
    detection_source: str
    affected_assets: List[str]
    tags: List[str]
    created_at: datetime
    updated_at: datetime
    resolved_at: Optional[datetime]
    resolution_notes: Optional[str]
    threat_details: Optional[Dict[str, Any]]
    mitigation_steps: Optional[List[str]]
    false_positive: bool
    reporter_id: str
    assigned_to: Optional[str]

    model_config = {
        "from_attributes": True
    }

class IncidentListResponse(BaseModel):
    """Schema for paginated incident list."""
    total: int
    items: List[IncidentResponse]
    page: int
    page_size: int

class TimeSeriesPoint(BaseModel):
    """Schema for a single point in time series data."""
    timestamp: str
    value: float

class TimeSeriesData(BaseModel):
    """Schema for time series analytics data."""
    metric: str
    interval: str
    time_range: str
    data: List[TimeSeriesPoint]

class ThreatAnalytics(BaseModel):
    """Schema for threat analytics overview."""
    total_requests: int
    blocked_requests: int
    block_rate: float
    avg_threat_score: float
    threat_distribution: Dict[str, int]
    time_range: str

class AttackDistribution(BaseModel):
    """Schema for attack distribution analytics."""
    attack_vectors: Dict[str, int] = Field(description="Count of each attack vector type")
    input_points: Dict[str, int] = Field(description="Count of each input point type")
    pattern_frequency: Dict[str, int] = Field(description="Frequency of each attack pattern")
    time_range: str

class ThreatSeverityStats(BaseModel):
    """Schema for threat severity statistics."""
    severity_distribution: Dict[str, int] = Field(
        description="Distribution of threats by severity level"
    )
    risk_factors: Dict[str, int] = Field(
        description="Count of each risk factor"
    )
    impact_scores: Dict[str, float] = Field(
        description="Average impact scores for CIA triad"
    )
    time_range: str

class GeoAnalytics(BaseModel):
    """Schema for geographic analytics."""
    ip_distribution: Dict[str, int] = Field(
        description="Distribution of IP versions"
    )
    platform_distribution: Dict[str, int] = Field(
        description="Distribution of client platforms"
    )
    proxy_usage: Dict[str, int] = Field(
        description="Count of proxy vs direct connections"
    )
    time_range: str

class SystemImpactAnalytics(BaseModel):
    """Schema for system impact analytics."""
    affected_systems: Dict[str, int] = Field(
        description="Count of affected systems"
    )
    mitigation_priorities: Dict[str, int] = Field(
        description="Distribution of mitigation priorities"
    )
    time_range: str

class UserMetrics(BaseModel):
    """Schema for user performance metrics."""
    total_responses: int
    avg_response_time: float
    avg_resolution_time: float
    response_distribution: Dict[str, int]

class UserAnalytics(BaseModel):
    """Schema for individual user analytics."""
    reported_incidents: Dict[str, Any] = Field(
        description="Statistics about incidents reported by the user"
    )
    assigned_incidents: Dict[str, Any] = Field(
        description="Statistics about incidents assigned to the user"
    )
    response_metrics: Dict[str, Any] = Field(
        description="User's incident response metrics"
    )
    time_range: str

class TeamMemberMetrics(BaseModel):
    """Schema for team member metrics."""
    name: str
    email: str
    department: Optional[str]
    role: Optional[str]
    metrics: UserMetrics

class TeamAnalytics(BaseModel):
    """Schema for team analytics."""
    team_members: int
    total_responses: int
    member_metrics: Dict[str, TeamMemberMetrics]
    workload_distribution: Dict[str, Any]
    time_range: str

class UserEngagementMetrics(BaseModel):
    """Schema for user engagement metrics."""
    name: str
    email: str
    metrics: Dict[str, int] = Field(
        description="Various engagement metrics counts"
    )

class UserEngagementAnalytics(BaseModel):
    """Schema for user engagement analytics."""
    user_engagement: Dict[str, UserEngagementMetrics]
    time_range: str

class UserPerformanceMetrics(BaseModel):
    """Schema for user performance analytics."""
    top_performers: List[Dict[str, Any]] = Field(
        description="List of top performing users with their metrics"
    )
    time_range: str

class UserInfo(BaseModel):
    """Schema for user information in recent incidents."""
    name: str
    email: str
    avatar: Optional[str] = None

class RecentIncident(BaseModel):
    """Schema for recent incident items."""
    id: str
    title: str
    status: str
    severity: str
    timestamp: str
    is_system_report: bool
    user: UserInfo

class RecentIncidentsResponse(BaseModel):
    """Schema for recent incidents response."""
    incidents: List[RecentIncident]
    total_count: int
    has_more: bool