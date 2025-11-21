"""Incident API routes.

This module provides FastAPI routes for managing security incidents.
"""

from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query, Path, status, Request, Header
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, and_
from datetime import datetime, timedelta
import humanize
import logging

from services.common.database.session import get_db
from services.common.models.incident import Incident, MaliciousRequest
from services.incident.core.incident_service import IncidentService
from services.user.core.user_service import UserService
from services.common.utils.input_sanitizer import sanitize_for_ml_analysis
from .schemas import (
    IncidentCreate,
    IncidentUpdate,
    IncidentResponse,
    MaliciousRequestCreate,
    ThreatAnalysisResponse,
    IncidentListResponse,
    RawRequestAnalysis,
    ThreatAnalytics,
    TimeSeriesData,
    AttackDistribution,
    ThreatSeverityStats,
    GeoAnalytics,
    SystemImpactAnalytics,
    RecentIncidentsResponse,
    RecentIncident,
    UserInfo
)

router = APIRouter(tags=["incidents"])

# Set up logger
logger = logging.getLogger(__name__)

def get_incident_service(db: Session = Depends(get_db)) -> IncidentService:
    """Get an instance of the IncidentService."""
    logger.debug("Creating new IncidentService instance")
    return IncidentService(db)

def get_user_service(db: Session = Depends(get_db)) -> UserService:
    """Get an instance of the UserService."""
    logger.debug("Creating new UserService instance")
    return UserService(db)

async def verify_api_key(
    x_api_key: str = Header(None),
    user_service: UserService = Depends(get_user_service)
):
    """Verify that the API key is valid and active."""
    logger.debug("Verifying API key")
    
    if not x_api_key:
        logger.error("Missing API key in request header")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key is required"
        )
        
    # Validate API key using user service
    logger.debug("Validating API key", extra={"key_prefix": x_api_key[:8]})
    if not await user_service.validate_api_key(x_api_key):
        logger.warning("Invalid or expired API key")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired API key"
        )
        
    logger.debug("API key validated successfully")
    return x_api_key

@router.get("/recent")
async def get_recent_incidents(
    limit: int = Query(10, ge=1, le=50),
    offset: int = Query(0, ge=0),
    service: IncidentService = Depends(get_incident_service),
    db: Session = Depends(get_db)
) -> RecentIncidentsResponse:
    """Get recent incidents with user information."""
    logger.debug("Accessing /recent endpoint", extra={"limit": limit, "offset": offset})
    return service.get_recent_incidents(limit=limit, offset=offset)

@router.get("/user/{user_id}/incidents", response_model=IncidentListResponse)
async def get_user_incidents(
    user_id: str = Path(..., description="ID of the user to fetch incidents for"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Number of items per page"),
    status: Optional[str] = Query(None, description="Filter by incident status"),
    severity: Optional[str] = Query(None, description="Filter by incident severity"),
    tag: Optional[str] = Query(None, description="Filter by incident tag"),
    service: IncidentService = Depends(get_incident_service),
    db: Session = Depends(get_db),
    api_key: str = Depends(verify_api_key)
) -> IncidentListResponse:
    """Get all incidents for a specific user with filtering and pagination."""
    logger.debug("Accessing /user/{user_id}/incidents endpoint", extra={"user_id": user_id})
    
    # Query base - filter by user_id
    query = db.query(Incident).filter(Incident.reporter_id == user_id)
    
    # Apply filters if provided
    if status:
        query = query.filter(Incident.status == status)
    if severity:
        query = query.filter(Incident.severity == severity)
    if tag:
        query = query.filter(Incident.tags.contains([tag]))
        
    # Calculate pagination
    total_items = query.count()
    total_pages = (total_items + page_size - 1) // page_size
    
    # Get paginated results
    incidents = query.order_by(desc(Incident.created_at))\
        .offset((page - 1) * page_size)\
        .limit(page_size)\
        .all()
        
    return IncidentListResponse(
        items=[IncidentResponse.from_orm(incident) for incident in incidents],
        total_items=total_items,
        total_pages=total_pages,
        current_page=page,
        page_size=page_size
    )

@router.post("/", response_model=IncidentResponse)
async def create_incident(
    incident: IncidentCreate,
    db: Session = Depends(get_db)
):
    """Create a new security incident."""
    service = IncidentService(db)
    return await service.create_incident(
        title=incident.title,
        description=incident.description,
        severity=incident.severity,
        detection_source=incident.detection_source or "manual",
        reporter_id=incident.reporter_id or "system",
        affected_assets=incident.affected_assets,
        tags=incident.tags
    )

@router.get("/", response_model=IncidentListResponse)
async def list_incidents(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: Optional[str] = Query(None),
    severity: Optional[str] = Query(None),
    tag: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    """List incidents with filtering and pagination."""
    service = IncidentService(db)
    return service.list_incidents(
        page=page,
        page_size=page_size,
        status=status,
        severity=severity,
        tag=tag
    )

@router.get("/{incident_id}", response_model=IncidentResponse)
async def get_incident(
    incident_id: str,
    db: Session = Depends(get_db)
):
    """Get details of a specific incident."""
    service = IncidentService(db)
    incident = service.get_incident(incident_id)
    
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    return incident

@router.put("/{incident_id}", response_model=IncidentResponse)
async def update_incident(
    incident_id: str,
    update: IncidentUpdate,
    db: Session = Depends(get_db)
):
    """Update an existing incident."""
    service = IncidentService(db)
    return service.update_incident(
        incident_id=incident_id,
        title=update.title,
        description=update.description,
        severity=update.severity,
        status=update.status,
        resolution_notes=update.resolution_notes,
        mitigation_steps=update.mitigation_steps,
        false_positive=update.false_positive
    )

@router.post("/analyze-request", response_model=ThreatAnalysisResponse)
async def analyze_request(
    request: MaliciousRequestCreate,
    service: IncidentService = Depends(get_incident_service),
    user_service: UserService = Depends(get_user_service),
    api_key: str = Depends(verify_api_key)
) -> Dict[str, Any]:
    """Analyze a request for security threats with enhanced threat intelligence."""
    logger.debug("Analyzing request", extra={"client_ip": request.client_ip})
    
    # Sanitize inputs before processing
    sanitized_data = sanitize_for_ml_analysis(
        client_ip=request.client_ip,
        request_path=request.request_path,
        request_method=request.request_method,
        request_headers=dict(request.request_headers),
        request_body=str(request.request_body) if request.request_body else None
    )
    
    # Get user from API key
    user = await user_service.get_user_by_api_key(api_key)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key"
        )
    
    # Extract user agent from sanitized headers
    user_agent = sanitized_data["request_headers"].get("User-Agent", "")
    
    # Perform enhanced analysis with threat intelligence using sanitized data
    analysis_result = await service.analyze_request(
        source_ip=request.client_ip,
        request_path=request.request_path,
        request_method=request.request_method,
        headers=request.request_headers,
        body=request.request_body,
        user_agent=user_agent
    )
    
    # Add user context to analysis
    analysis_result["analyzed_by"] = user.id
    analysis_result["analysis_timestamp"] = datetime.utcnow().isoformat()
    
    # Create malicious request record if threat detected
    if analysis_result["threat_score"] > 0:
        malicious_request = service.add_malicious_request(
            source_ip=request.client_ip,
            request_path=request.request_path,
            request_method=request.request_method,
            threat_type=analysis_result["threat_type"],
            threat_score=analysis_result["threat_score"],
            headers=request.request_headers,
            body=request.request_body,
            user_agent=user_agent,
            threat_details={
                "analysis_methods": analysis_result.get("analysis_methods", []),
                "static_analysis": analysis_result.get("static_analysis", {}),
                "threat_intelligence_analysis": analysis_result.get("threat_intelligence_analysis", {}),
                "confidence": analysis_result.get("confidence", 0.0),
                "recommendations": analysis_result.get("recommendations", [])
            }
        )
        analysis_result["malicious_request_id"] = malicious_request.id
    
    logger.debug("Analysis complete", extra={"threat_score": analysis_result['threat_score']})
    return analysis_result

@router.post("/analyze/raw", response_model=ThreatAnalysisResponse)
async def analyze_raw_request(
    request: Request,
    db: Session = Depends(get_db)
):
    """Analyze a raw request from middleware for security threats."""
    service = IncidentService(db)
    
    # Get request body if present
    body = None
    if request.method in ["POST", "PUT", "PATCH"]:
        try:
            body = await request.json()
        except:
            try:
                body = await request.body()
            except:
                pass

    # Add client IP to headers for analysis
    headers = dict(request.headers)
    headers["x-forwarded-for"] = request.client.host

    analysis = await service.analyze_raw_request(
        method=request.method,
        url=str(request.url),
        path=request.url.path,
        headers=headers,
        body=body,
        query_params=dict(request.query_params)
    )
    
    return ThreatAnalysisResponse(
        threat_score=analysis["threat_score"],
        threat_type=analysis["threat_type"],
        findings=analysis["findings"],
        should_block=analysis["should_block"]
    )

@router.post("/analyze/service", response_model=ThreatAnalysisResponse)
async def analyze_service_request(
    raw_request: Dict[str, Any],
    request: Request,
    db: Session = Depends(get_db)
):
    """Analyze requests forwarded from other backend services."""
    service = IncidentService(db)
    
    # Verify API key
    api_key = request.headers.get("x-api-key")
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key is required"
        )
    
    # Get service name from headers
    service_name = request.headers.get("x-service-name", "unknown-service")
    
    # Extract common fields based on framework
    method = None
    url = None
    headers = {}
    body = None
    client_ip = None
    query_params = {}
    
    # Express.js request format
    if "originalUrl" in raw_request:
        method = raw_request.get("method")
        url = raw_request.get("originalUrl") or raw_request.get("url")
        headers = raw_request.get("headers", {})
        body = raw_request.get("body")
        client_ip = (
            raw_request.get("ip") or 
            # Only trust x-forwarded-for if explicitly configured/validated in production
            # For now, we prioritize direct IP or connection address
            raw_request.get("connection", {}).get("remoteAddress") or
            headers.get("x-forwarded-for", "").split(",")[0].strip()
        )
        query_params = raw_request.get("query", {})
    
    # Actix-web request format
    elif "_method" in raw_request:
        method = raw_request.get("_method")
        url = raw_request.get("uri", "")
        headers = raw_request.get("headers", {})
        body = raw_request.get("payload")
        client_ip = headers.get("x-forwarded-for", "").split(",")[0].strip()
        query_params = dict(item.split("=") for item in url.split("?")[1].split("&")) if "?" in url else {}
    
    # Axum request format
    elif "uri" in raw_request and "version" in raw_request:
        method = raw_request.get("method")
        url = raw_request.get("uri")
        headers = raw_request.get("headers", {})
        body = raw_request.get("body")
        client_ip = headers.get("x-forwarded-for", "").split(",")[0].strip()
        query_params = raw_request.get("query", {})
    
    # Generic/unknown format
    else:
        method = raw_request.get("method") or raw_request.get("_method")
        url = raw_request.get("url") or raw_request.get("uri") or raw_request.get("path") or ""
        headers = raw_request.get("headers", {})
        body = raw_request.get("body") or raw_request.get("payload") or raw_request.get("data")
        client_ip = (
            raw_request.get("ip") or 
            raw_request.get("clientIp") or 
            raw_request.get("remoteAddress") or
            headers.get("x-forwarded-for", "").split(",")[0].strip()
        )
        query_params = raw_request.get("query") or raw_request.get("queryParams") or raw_request.get("params") or {}
    
    # Analyze the request
    analysis = await service.analyze_raw_request(
        method=method,
        url=url,
        path=url.split("?")[0] if url else "",
        headers=headers,
        body=body,
        query_params=query_params,
        client_ip=client_ip
    )
    
    # Add service context to findings if threat detected
    if analysis["threat_score"] > 0:
        service_context = f"Detected in {service_name}"
        analysis["findings"].append(service_context)
    
    return ThreatAnalysisResponse(
        threat_score=analysis["threat_score"],
        threat_type=analysis["threat_type"],
        findings=analysis["findings"],
        should_block=analysis["should_block"]
    )

# Analytics endpoints

def _get_time_threshold(time_range: str) -> datetime:
    """Helper to get datetime threshold from time range string."""
    now = datetime.utcnow()
    if time_range == "24h":
        return now - timedelta(hours=24)
    elif time_range == "7d":
        return now - timedelta(days=7)
    elif time_range == "30d":
        return now - timedelta(days=30)
    return datetime.min

@router.get("/analytics/overview", response_model=ThreatAnalytics)
async def get_threat_analytics(
    time_range: str = Query("24h", description="Time range (24h, 7d, 30d, all)"),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Get overview of threat analytics."""
    threshold = _get_time_threshold(time_range)

    # Query base - filter by time
    query = db.query(MaliciousRequest).filter(
        MaliciousRequest.timestamp >= threshold
    )
    
    # Get total requests and blocked requests
    total_requests = query.count()
    blocked_requests = query.filter(MaliciousRequest.is_blocked == True).count()
    
    # Get average threat score
    avg_threat_score = db.query(func.avg(MaliciousRequest.threat_score)).scalar() or 0
    
    # Get threat type distribution
    threat_types = db.query(
        MaliciousRequest.threat_type,
        func.count(MaliciousRequest.id).label('count')
    ).group_by(MaliciousRequest.threat_type).all()
    
    return {
        "total_requests": total_requests,
        "blocked_requests": blocked_requests,
        "block_rate": (blocked_requests / total_requests * 100) if total_requests > 0 else 0,
        "avg_threat_score": float(avg_threat_score),
        "threat_distribution": {t[0]: t[1] for t in threat_types},
        "time_range": time_range
    }

@router.get("/analytics/time-series", response_model=TimeSeriesData)
async def get_time_series_data(
    metric: str = Query("threats", description="Metric to analyze (threats, blocks, score)"),
    interval: str = Query("1h", description="Time interval (1h, 1d, 1w)"),
    time_range: str = Query("24h", description="Time range (24h, 7d, 30d)"),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Get time series data for threats."""
    threshold = _get_time_threshold(time_range)
    
    # Determine group format based on interval/db type (assuming SQLite/MySQL/PG compatibility needs)
    # For simplicity using MySQL/SQLite compatible format if possible, or just Python processing if volume is low.
    # But here we want optimization.
    # Assuming MySQL for now based on previous context (MySQL mentioned in summary).
    
    if time_range == "24h":
        group_format = "%Y-%m-%d %H:00:00"
    else:
        group_format = "%Y-%m-%d"

    # Base query
    query = db.query(
        func.date_format(MaliciousRequest.timestamp, group_format).label('time_bucket'),
        func.count(MaliciousRequest.id).label('count'),
        func.avg(MaliciousRequest.threat_score).label('avg_score')
    ).filter(MaliciousRequest.timestamp >= threshold)

    # Add metric-specific filters
    if metric == "blocks":
        query = query.filter(MaliciousRequest.is_blocked == True)

    # Group and order
    results = query.group_by('time_bucket').order_by('time_bucket').all()

    return {
        "metric": metric,
        "interval": interval,
        "time_range": time_range,
        "data": [
            {
                "timestamp": r[0],
                "value": float(r[2]) if metric == "score" else int(r[1])
            } for r in results
        ]
    }

@router.get("/analytics/attack-distribution", response_model=AttackDistribution)
async def get_attack_distribution(
    time_range: str = Query("24h", description="Time range (24h, 7d, 30d, all)"),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Get distribution of attack vectors and patterns."""
    threshold = _get_time_threshold(time_range)
    
    # Attack vectors (detection_source)
    vectors = db.query(
        Incident.detection_source,
        func.count(Incident.id)
    ).filter(
        Incident.created_at >= threshold
    ).group_by(Incident.detection_source).all()
    
    attack_vectors = {v[0] or "unknown": v[1] for v in vectors}
    
    # Fetch only necessary columns for input points and patterns
    incidents = db.query(Incident.affected_assets, Incident.tags).filter(
        Incident.created_at >= threshold
    ).all()
    
    input_points = {}
    pattern_frequency = {}
    
    for assets, tags in incidents:
        # Process assets
        if assets:
            asset_list = assets if isinstance(assets, list) else [str(a) for a in str(assets).split(',')]
            for asset in asset_list:
                if asset:
                    input_points[asset] = input_points.get(asset, 0) + 1
                    
        # Process tags
        if tags:
            tag_list = tags if isinstance(tags, list) else [str(t) for t in str(tags).split(',')]
            for tag in tag_list:
                if tag:
                    pattern = tag.replace("attack:", "") if tag.startswith("attack:") else tag
                    pattern_frequency[pattern] = pattern_frequency.get(pattern, 0) + 1
                    
    return {
        "attack_vectors": attack_vectors,
        "input_points": input_points,
        "pattern_frequency": pattern_frequency,
        "time_range": time_range
    }