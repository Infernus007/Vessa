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
    print("[DEBUG] Creating new IncidentService instance")
    return IncidentService(db)

def get_user_service(db: Session = Depends(get_db)) -> UserService:
    """Get an instance of the UserService."""
    print("[DEBUG] Creating new UserService instance")
    return UserService(db)

async def verify_api_key(
    x_api_key: str = Header(None),
    user_service: UserService = Depends(get_user_service)
):
    """Verify that the API key is valid and active.
    
    Args:
        x_api_key: API key from request header
        user_service: User service instance for validation
        
    Returns:
        str: The validated API key
        
    Raises:
        HTTPException: If API key is missing or invalid
    """
    print("[DEBUG] Verifying API key")
    
    if not x_api_key:
        print("[ERROR] Missing API key in request header")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key is required"
        )
        
    # Validate API key using user service
    print(f"[DEBUG] Validating API key: {x_api_key[:8]}...")
    if not await user_service.validate_api_key(x_api_key):
        print("[ERROR] Invalid or expired API key")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired API key"
        )
        
    print("[DEBUG] API key validated successfully")
    return x_api_key

@router.get("/recent", response_model=RecentIncidentsResponse)
async def get_recent_incidents(
    limit: int = Query(10, ge=1, le=50),
    offset: int = Query(0, ge=0),
    service: IncidentService = Depends(get_incident_service),
    db: Session = Depends(get_db)
) -> RecentIncidentsResponse:
    """Get recent incidents with user information.
    
    Args:
        limit: Maximum number of incidents to return
        offset: Number of incidents to skip
        service: Incident service instance
        db: Database session
    
    Returns:
        List of recent incidents with user information
    """
    print(f"[DEBUG] Accessing /recent endpoint with limit={limit}, offset={offset}")
    
    # Check if we have any incidents in the database
    incident_count = db.query(Incident).count()
    print(f"[DEBUG] Total incidents in database: {incident_count}")
    
    result = service.get_recent_incidents(limit=limit, offset=offset)
    print(f"[DEBUG] Service returned result: {result}")
    
    return RecentIncidentsResponse(**result)

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
    """Get all incidents for a specific user with filtering and pagination.
    
    Args:
        user_id: ID of the user to fetch incidents for
        page: Page number for pagination
        page_size: Number of items per page
        status: Optional filter by incident status
        severity: Optional filter by incident severity
        tag: Optional filter by incident tag
        service: Incident service instance
        db: Database session
        api_key: API key for authentication
    
    Returns:
        List of incidents for the specified user
    """
    print(f"[DEBUG] Accessing /user/{user_id}/incidents endpoint")
    print(f"[DEBUG] Query params: page={page}, page_size={page_size}, status={status}, severity={severity}, tag={tag}")
    
    try:
        # Query base - filter by user_id
        query = db.query(Incident).filter(Incident.reporter_id == user_id)
        print(f"[DEBUG] Base query created for user_id: {user_id}")
        
        # Apply filters if provided
        if status:
            query = query.filter(Incident.status == status)
            print(f"[DEBUG] Applied status filter: {status}")
        if severity:
            query = query.filter(Incident.severity == severity)
            print(f"[DEBUG] Applied severity filter: {severity}")
        if tag:
            query = query.filter(Incident.tags.contains([tag]))
            print(f"[DEBUG] Applied tag filter: {tag}")
            
        # Calculate pagination
        total_items = query.count()
        total_pages = (total_items + page_size - 1) // page_size
        print(f"[DEBUG] Pagination stats: total_items={total_items}, total_pages={total_pages}")
        
        # Get paginated results
        incidents = query.order_by(desc(Incident.created_at))\
            .offset((page - 1) * page_size)\
            .limit(page_size)\
            .all()
        print(f"[DEBUG] Retrieved {len(incidents)} incidents for page {page}")
            
        response = IncidentListResponse(
            items=[IncidentResponse.from_orm(incident) for incident in incidents],
            total_items=total_items,
            total_pages=total_pages,
            current_page=page,
            page_size=page_size
        )
        print("[DEBUG] Successfully created response object")
        return response
        
    except Exception as e:
        print(f"[ERROR] Error fetching incidents for user {user_id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching incidents for user {user_id}: {str(e)}"
        )

@router.post("/", response_model=IncidentResponse)
async def create_incident(
    incident: IncidentCreate,
    db: Session = Depends(get_db)
):
    """Create a new security incident."""
    service = IncidentService(db)
    
    try:
        incident_obj = await service.create_incident(
            title=incident.title,
            description=incident.description,
            severity=incident.severity,
            detection_source=incident.detection_source or "manual",  # Default to manual if not provided
            reporter_id=incident.reporter_id or "system",  # Default to system if not provided
            affected_assets=incident.affected_assets,
            tags=incident.tags
        )
        return incident_obj
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

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
    
    try:
        return service.list_incidents(
            page=page,
            page_size=page_size,
            status=status,
            severity=severity,
            tag=tag
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

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
    
    try:
        incident = service.update_incident(
            incident_id=incident_id,
            title=update.title,
            description=update.description,
            severity=update.severity,
            status=update.status,
            resolution_notes=update.resolution_notes,
            mitigation_steps=update.mitigation_steps,
            false_positive=update.false_positive
        )
        return incident
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/analyze-request", response_model=ThreatAnalysisResponse)
async def analyze_request(
    request: MaliciousRequestCreate,
    service: IncidentService = Depends(get_incident_service),
    user_service: UserService = Depends(get_user_service),
    api_key: str = Depends(verify_api_key)
) -> Dict[str, Any]:
    """Analyze a request for security threats with enhanced threat intelligence.
    
    This endpoint now includes:
    - Static pattern analysis
    - Machine learning analysis (if enabled)
    - Threat intelligence analysis (IP/domain/URL reputation, YARA rules)
    - Comprehensive threat scoring
    
    Args:
        request: Request data to analyze
        service: Incident service instance
        user_service: User service instance
        api_key: API key for authentication
    
    Returns:
        Enhanced threat analysis results
    """
    print(f"[DEBUG] Analyzing request from {request.client_ip}")
    
    try:
        # Get user from API key
        user = await user_service.get_user_by_api_key(api_key)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid API key"
            )
        
        # Extract user agent from headers
        user_agent = request.request_headers.get("User-Agent", "")
        
        # Perform enhanced analysis with threat intelligence
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
        
        print(f"[DEBUG] Analysis complete. Threat score: {analysis_result['threat_score']}")
        return analysis_result
        
    except Exception as e:
        print(f"[ERROR] Request analysis failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Analysis failed: {str(e)}"
        )

@router.post("/analyze/raw", response_model=ThreatAnalysisResponse)
async def analyze_raw_request(
    request: Request,
    db: Session = Depends(get_db)
):
    """Analyze a raw request from middleware for security threats.
    
    This endpoint accepts the raw FastAPI Request object directly.
    No transformation needed in middleware - just forward the entire request.
    
    Example middleware integration:
    ```python
    async def security_middleware(request: Request, call_next):
        # Forward the entire request object
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "http://localhost:8000/incidents/analyze/raw",
                headers=dict(request.headers),
                content=await request.body()
            )
            result = response.json()
            
        # Block request if needed
        if result["should_block"]:
            raise HTTPException(
                status_code=403, 
                detail={
                    "message": "Request blocked by security rules",
                    "findings": result["findings"]
                }
            )
            
        return await call_next(request)
    ```
    """
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
    """Analyze requests forwarded from other backend services.
    
    This endpoint accepts the raw middleware request object from any backend service.
    Just forward the entire request object as you receive it in your middleware.
    
    Example Node.js/Express middleware:
    ```javascript
    app.use(async (req, res, next) => {
        try {
            const response = await fetch('https://your-security-service/incidents/analyze/service', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-API-Key': 'your-api-key',
                    'X-Service-Name': 'payment-service'
                },
                body: JSON.stringify(req)  // Just forward the entire request object
            });
            
            const result = await response.json();
            if (result.should_block) {
                return res.status(403).json({
                    error: 'Request blocked by security service',
                    findings: result.findings
                });
            }
            next();
        } catch (error) {
            next();
        }
    });
    ```

    Example Rust/Actix middleware:
    ```rust
    async fn security_middleware(req: ServiceRequest) -> Result<ServiceResponse, Error> {
        let client = Client::new();
        
        // Forward the entire request object
        let response = client
            .post("https://your-security-service/incidents/analyze/service")
            .header("X-API-Key", "your-api-key")
            .header("X-Service-Name", "auth-service")
            .json(&req)  // ServiceRequest implements Serialize
            .send()
            .await?;
            
        let result = response.json::<SecurityResponse>().await?;
        if result.should_block {
            return Ok(req.into_response(
                HttpResponse::Forbidden()
                    .json(json!({
                        "error": "Request blocked by security service",
                        "findings": result.findings
                    }))
                    .into_body(),
            ));
        }

        Ok(req.into_response(next.call(req).await?.into_body()))
    }
    ```
    """
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
    # We'll detect the framework and extract accordingly
    method = None
    url = None
    headers = {}
    body = None
    client_ip = None
    query_params = {}
    
    # Express.js request format
    if "originalUrl" in raw_request:  # Express.js specific
        method = raw_request.get("method")
        url = raw_request.get("originalUrl") or raw_request.get("url")
        headers = raw_request.get("headers", {})
        body = raw_request.get("body")
        client_ip = (
            raw_request.get("ip") or 
            headers.get("x-forwarded-for", "").split(",")[0].strip() or 
            raw_request.get("connection", {}).get("remoteAddress")
        )
        query_params = raw_request.get("query", {})
    
    # Actix-web request format
    elif "_method" in raw_request:  # Actix specific
        method = raw_request.get("_method")
        url = raw_request.get("uri", "")
        headers = raw_request.get("headers", {})
        body = raw_request.get("payload")
        client_ip = headers.get("x-forwarded-for", "").split(",")[0].strip()
        query_params = dict(item.split("=") for item in url.split("?")[1].split("&")) if "?" in url else {}
    
    # Axum request format
    elif "uri" in raw_request and "version" in raw_request:  # Axum specific
        method = raw_request.get("method")
        url = raw_request.get("uri")
        headers = raw_request.get("headers", {})
        body = raw_request.get("body")
        client_ip = headers.get("x-forwarded-for", "").split(",")[0].strip()
        query_params = raw_request.get("query", {})
    
    # Generic/unknown format - try common fields
    else:
        method = raw_request.get("method") or raw_request.get("_method")
        url = (
            raw_request.get("url") or 
            raw_request.get("uri") or 
            raw_request.get("path") or 
            ""
        )
        headers = raw_request.get("headers", {})
        body = (
            raw_request.get("body") or 
            raw_request.get("payload") or 
            raw_request.get("data")
        )
        client_ip = (
            raw_request.get("ip") or 
            raw_request.get("clientIp") or 
            raw_request.get("remoteAddress") or
            headers.get("x-forwarded-for", "").split(",")[0].strip()
        )
        query_params = (
            raw_request.get("query") or 
            raw_request.get("queryParams") or 
            raw_request.get("params") or 
            {}
        )
    
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
@router.get("/analytics/overview", response_model=ThreatAnalytics)
async def get_threat_analytics(
    time_range: str = Query("24h", description="Time range (24h, 7d, 30d, all)"),
    db: Session = Depends(get_db),
    api_key: str = Depends(verify_api_key)
) -> Dict[str, Any]:
    """Get overview of threat analytics."""
    # Calculate time threshold based on range
    now = datetime.utcnow()
    if time_range == "24h":
        threshold = now - timedelta(hours=24)
    elif time_range == "7d":
        threshold = now - timedelta(days=7)
    elif time_range == "30d":
        threshold = now - timedelta(days=30)
    else:
        threshold = datetime.min

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
    now = datetime.utcnow()
    
    # Calculate time threshold and interval
    if time_range == "24h":
        threshold = now - timedelta(hours=24)
        group_format = "%Y-%m-%d %H:00:00"
    elif time_range == "7d":
        threshold = now - timedelta(days=7)
        group_format = "%Y-%m-%d"
    else:  # 30d
        threshold = now - timedelta(days=30)
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
    print("\n[DEBUG] === Starting Attack Distribution Analysis ===")
    
    threshold = _get_time_threshold(time_range)
    print(f"[DEBUG] Time threshold: {threshold}")
    
    try:
        # Get all incidents within time range
        query = db.query(Incident).filter(Incident.created_at >= threshold)
        print(f"[DEBUG] SQL Query: {query}")
        
        incidents = query.all()
        print(f"[DEBUG] Found {len(incidents)} incidents")
        
        if len(incidents) == 0:
            print("[DEBUG] No incidents found in the specified time range")
            return {
                "attack_vectors": {},
                "input_points": {},
                "pattern_frequency": {},
                "time_range": time_range
            }
        
        # Initialize counters
        attack_vectors = {}
        input_points = {}
        pattern_frequency = {}
        
        for idx, incident in enumerate(incidents):
            print(f"\n[DEBUG] Processing incident {idx + 1}/{len(incidents)}")
            print(f"[DEBUG] Incident ID: {incident.id}")
            print(f"[DEBUG] Title: {incident.title}")
            print(f"[DEBUG] Created At: {incident.created_at}")
            print(f"[DEBUG] Detection Source: {incident.detection_source}")
            print(f"[DEBUG] Affected Assets Type: {type(incident.affected_assets)}")
            print(f"[DEBUG] Affected Assets: {incident.affected_assets}")
            print(f"[DEBUG] Tags Type: {type(incident.tags)}")
            print(f"[DEBUG] Tags: {incident.tags}")
            
            try:
                # Process detection source
                if incident.detection_source:
                    source = str(incident.detection_source).strip()
                    if source:
                        attack_vectors[source] = attack_vectors.get(source, 0) + 1
                        print(f"[DEBUG] Added attack vector: {source}")
                else:
                    attack_vectors["unknown"] = attack_vectors.get("unknown", 0) + 1
                    print("[DEBUG] Added unknown attack vector")
                
                # Process affected assets
                assets = incident.affected_assets
                if assets:
                    if isinstance(assets, str):
                        assets = [assets]  # Convert string to list
                    elif isinstance(assets, list):
                        assets = [str(asset).strip() for asset in assets if asset]
                    
                    for asset in assets:
                        if asset:
                            input_points[asset] = input_points.get(asset, 0) + 1
                            print(f"[DEBUG] Added input point: {asset}")
                
                # Process tags
                tags = incident.tags
                if tags:
                    if isinstance(tags, str):
                        tags = [tags]  # Convert string to list
                    elif isinstance(tags, list):
                        tags = [str(tag).strip() for tag in tags if tag]
                    
                    for tag in tags:
                        if tag:
                            if tag.startswith("attack:"):
                                pattern = tag.replace("attack:", "")
                            else:
                                pattern = tag
                            pattern_frequency[pattern] = pattern_frequency.get(pattern, 0) + 1
                            print(f"[DEBUG] Added pattern: {pattern}")
            
            except Exception as e:
                print(f"[ERROR] Error processing incident {incident.id}: {str(e)}")
                continue
        
        result = {
            "attack_vectors": attack_vectors,
            "input_points": input_points,
            "pattern_frequency": pattern_frequency,
            "time_range": time_range
        }
        
        print("\n[DEBUG] === Final Results ===")
        print(f"[DEBUG] Attack Vectors: {attack_vectors}")
        print(f"[DEBUG] Input Points: {input_points}")
        print(f"[DEBUG] Pattern Frequency: {pattern_frequency}")
        
        return result
        
    except Exception as e:
        print(f"[ERROR] Unexpected error in get_attack_distribution: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error processing attack distribution: {str(e)}"
        )

@router.get("/analytics/severity", response_model=ThreatSeverityStats)
async def get_severity_statistics(
    time_range: str = Query("24h", description="Time range (24h, 7d, 30d, all)"),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Get threat severity statistics."""
    threshold = _get_time_threshold(time_range)
    print("hi")
    # Get requests with threat details
    requests = db.query(MaliciousRequest).filter(
        MaliciousRequest.timestamp >= threshold,
        MaliciousRequest.threat_details.isnot(None)
    ).all()
    
    severity_distribution = {"critical": 0, "high": 0, "medium": 0, "low": 0}
    risk_factors = {}
    impact_scores = {"confidentiality": 0, "integrity": 0, "availability": 0}
    total_requests = len(requests)
    
    for req in requests:
        if not req.threat_details:
            continue
            
        # Get risk assessment
        risk = req.threat_details.get("risk_assessment", {})
        severity_distribution[risk.get("level", "medium")] += 1
        
        # Aggregate risk factors
        for factor in risk.get("factors", []):
            factor_name = factor.get("factor", "unknown")
            risk_factors[factor_name] = risk_factors.get(factor_name, 0) + 1
            
        # Aggregate impact scores
        impact = risk.get("potential_impact", {})
        impact_scores["confidentiality"] += impact.get("confidentiality", 0)
        impact_scores["integrity"] += impact.get("integrity", 0)
        impact_scores["availability"] += impact.get("availability", 0)
    
    # Normalize impact scores
    if total_requests > 0:
        for key in impact_scores:
            impact_scores[key] /= total_requests
    
    return {
        "severity_distribution": severity_distribution,
        "risk_factors": risk_factors,
        "impact_scores": impact_scores,
        "time_range": time_range
    }

@router.get("/analytics/geo", response_model=GeoAnalytics)
async def get_geo_analytics(
    time_range: str = Query("24h", description="Time range (24h, 7d, 30d, all)"),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Get geographic distribution of threats."""
    threshold = _get_time_threshold(time_range)
    
    # Get requests with client info
    requests = db.query(MaliciousRequest).filter(
        MaliciousRequest.timestamp >= threshold,
        MaliciousRequest.threat_details.isnot(None)
    ).all()
    
    ip_distribution = {}
    platform_distribution = {}
    proxy_usage = {"proxy": 0, "direct": 0}
    
    for req in requests:
        if not req.threat_details or "request_context" not in req.threat_details:
            continue
            
        client_info = req.threat_details["request_context"].get("client_info", {})
        
        # Aggregate IP data
        ip_version = client_info.get("ip_version", "unknown")
        ip_distribution[ip_version] = ip_distribution.get(ip_version, 0) + 1
        
        # Aggregate platform data
        platform = client_info.get("platform", "unknown")
        platform_distribution[platform] = platform_distribution.get(platform, 0) + 1
        
        # Count proxy usage
        if client_info.get("is_proxy", False):
            proxy_usage["proxy"] += 1
        else:
            proxy_usage["direct"] += 1
    
    return {
        "ip_distribution": ip_distribution,
        "platform_distribution": platform_distribution,
        "proxy_usage": proxy_usage,
        "time_range": time_range
    }

@router.get("/analytics/system-impact", response_model=SystemImpactAnalytics)
async def get_system_impact(
    time_range: str = Query("24h", description="Time range (24h, 7d, 30d, all)"),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Get system impact analytics."""
    threshold = _get_time_threshold(time_range)
    
    # Get requests with threat details
    requests = db.query(MaliciousRequest).filter(
        MaliciousRequest.timestamp >= threshold,
        MaliciousRequest.threat_details.isnot(None)
    ).all()
    
    affected_systems = {}
    mitigation_priorities = {"immediate": 0, "high": 0, "normal": 0}
    
    for req in requests:
        if not req.threat_details:
            continue
            
        # Get impact assessment
        impact = req.threat_details.get("risk_assessment", {}).get("potential_impact", {})
        
        # Aggregate affected systems
        for system in impact.get("affected_systems", []):
            affected_systems[system] = affected_systems.get(system, 0) + 1
            
        # Count mitigation priorities
        priority = req.threat_details.get("risk_assessment", {}).get("mitigation_priority", "normal")
        mitigation_priorities[priority] = mitigation_priorities.get(priority, 0) + 1
    
    return {
        "affected_systems": affected_systems,
        "mitigation_priorities": mitigation_priorities,
        "time_range": time_range
    }

# User Analytics Endpoints
@router.get("/analytics/users/{user_id}", response_model=Dict[str, Any])
async def get_user_analytics(
    user_id: str,
    time_range: str = Query("30d", description="Time range (24h, 7d, 30d, all)"),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Get analytics for a specific user."""
    service = IncidentService(db)
    return service.get_user_analytics(user_id, time_range)

@router.get("/analytics/team", response_model=Dict[str, Any])
async def get_team_analytics(
    time_range: str = Query("30d", description="Time range (24h, 7d, 30d, all)"),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Get analytics for the entire team."""
    service = IncidentService(db)
    return service.get_team_analytics(time_range)

@router.get("/analytics/engagement", response_model=Dict[str, Any])
async def get_user_engagement(
    time_range: str = Query("30d", description="Time range (24h, 7d, 30d, all)"),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Get user engagement metrics."""
    service = IncidentService(db)
    return service.get_user_engagement_metrics(time_range)

@router.get("/analytics/user-performance", response_model=Dict[str, Any])
async def get_user_performance_metrics(
    time_range: str = Query("30d", description="Time range (24h, 7d, 30d, all)"),
    top_n: int = Query(5, description="Number of top performers to return"),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Get performance metrics for all users."""
    service = IncidentService(db)
    print("hi")
    team_analytics = service.get_team_analytics(time_range)
    
    # Extract and sort user metrics by total responses
    user_metrics = team_analytics["member_metrics"]
    sorted_users = sorted(
        user_metrics.items(),
        key=lambda x: x[1]["metrics"]["total_responses"],
        reverse=True
    )[:top_n]
    
    return {
        "top_performers": [
            {
                "user_id": user_id,
                "name": metrics["name"],
                "email": metrics["email"],
                "department": metrics["department"],
                "role": metrics["role"],
                "metrics": metrics["metrics"]
            }
            for user_id, metrics in sorted_users
        ],
        "time_range": time_range
    }

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