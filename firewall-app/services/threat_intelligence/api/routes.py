"""Threat Intelligence API routes.

This module provides FastAPI routes for threat intelligence services.
"""

from typing import Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status, Header
from sqlalchemy.orm import Session
from datetime import datetime

from services.common.database.session import get_db
from services.threat_intelligence.core.threat_intelligence_service import ThreatIntelligenceService
from services.user.core.user_service import UserService
from .schemas import (
    IPReputationRequest,
    IPReputationResponse,
    DomainReputationRequest,
    DomainReputationResponse,
    URLReputationRequest,
    URLReputationResponse,
    ThreatAnalysisRequest,
    ThreatAnalysisResponse,
    YARAMatchRequest,
    YARAMatchResponse
)

router = APIRouter(tags=["threat-intelligence"])

def get_threat_intelligence_service() -> ThreatIntelligenceService:
    """Get an instance of the ThreatIntelligenceService."""
    return ThreatIntelligenceService()

def get_user_service(db: Session = Depends(get_db)) -> UserService:
    """Get an instance of the UserService."""
    return UserService(db)

async def verify_api_key(
    x_api_key: str = Header(None),
    user_service: UserService = Depends(get_user_service)
):
    """Verify that the API key is valid and active."""
    if not x_api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key is required"
        )
        
    if not await user_service.validate_api_key(x_api_key):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired API key"
        )
        
    return x_api_key

@router.post("/ip-reputation", response_model=IPReputationResponse)
async def check_ip_reputation(
    request: IPReputationRequest,
    service: ThreatIntelligenceService = Depends(get_threat_intelligence_service),
    api_key: str = Depends(verify_api_key)
) -> IPReputationResponse:
    """Check IP reputation.
    
    Args:
        request: IP reputation request
        service: Threat intelligence service instance
        api_key: API key for authentication
    
    Returns:
        IP reputation analysis results
    """
    try:
        async with service:
            reputation_data = await service.check_ip_reputation(request.ip)
            return IPReputationResponse(**reputation_data)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error checking IP reputation: {str(e)}"
        )

@router.post("/domain-reputation", response_model=DomainReputationResponse)
async def check_domain_reputation(
    request: DomainReputationRequest,
    service: ThreatIntelligenceService = Depends(get_threat_intelligence_service),
    api_key: str = Depends(verify_api_key)
) -> DomainReputationResponse:
    """Check domain reputation.
    
    Args:
        request: Domain reputation request
        service: Threat intelligence service instance
        api_key: API key for authentication
    
    Returns:
        Domain reputation analysis results
    """
    try:
        async with service:
            reputation_data = await service.check_domain_reputation(request.domain)
            return DomainReputationResponse(**reputation_data)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error checking domain reputation: {str(e)}"
        )

@router.post("/url-reputation", response_model=URLReputationResponse)
async def check_url_reputation(
    request: URLReputationRequest,
    service: ThreatIntelligenceService = Depends(get_threat_intelligence_service),
    api_key: str = Depends(verify_api_key)
) -> URLReputationResponse:
    """Check URL reputation.
    
    Args:
        request: URL reputation request
        service: Threat intelligence service instance
        api_key: API key for authentication
    
    Returns:
        URL reputation analysis results
    """
    try:
        async with service:
            reputation_data = await service.check_url_reputation(request.url)
            return URLReputationResponse(**reputation_data)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error checking URL reputation: {str(e)}"
        )

@router.post("/yara-match", response_model=YARAMatchResponse)
async def match_yara_rules(
    request: YARAMatchRequest,
    service: ThreatIntelligenceService = Depends(get_threat_intelligence_service),
    api_key: str = Depends(verify_api_key)
) -> YARAMatchResponse:
    """Match content against YARA rules.
    
    Args:
        request: YARA match request
        service: Threat intelligence service instance
        api_key: API key for authentication
    
    Returns:
        YARA rule matching results
    """
    try:
        yara_data = service.match_yara_rules(request.content)
        return YARAMatchResponse(**yara_data)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error matching YARA rules: {str(e)}"
        )

@router.post("/comprehensive-analysis", response_model=ThreatAnalysisResponse)
async def get_comprehensive_analysis(
    request: ThreatAnalysisRequest,
    service: ThreatIntelligenceService = Depends(get_threat_intelligence_service),
    api_key: str = Depends(verify_api_key)
) -> ThreatAnalysisResponse:
    """Get comprehensive threat analysis.
    
    Args:
        request: Comprehensive analysis request
        service: Threat intelligence service instance
        api_key: API key for authentication
    
    Returns:
        Comprehensive threat analysis results
    """
    try:
        async with service:
            analysis_data = await service.get_comprehensive_threat_analysis(
                ip=request.ip,
                domain=request.domain,
                url=request.url,
                content=request.content
            )
            return ThreatAnalysisResponse(**analysis_data)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error performing comprehensive analysis: {str(e)}"
        )

@router.get("/health")
async def health_check():
    """Health check endpoint for threat intelligence service."""
    return {
        "status": "healthy",
        "service": "threat-intelligence",
        "timestamp": datetime.now().isoformat()
    } 