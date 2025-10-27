"""WAF Engine - Core request analysis and decision engine.

This module provides the main WAF engine that analyzes requests and makes
blocking decisions in real-time.
"""

import asyncio
import hashlib
import time
from typing import Dict, Any, Optional, Tuple
from datetime import datetime
import logging
from dataclasses import dataclass

from .waf_config import WAFConfig, WAFAction, BlockingMode
from services.incident.core.incident_service import IncidentService

logger = logging.getLogger(__name__)


@dataclass
class WAFDecision:
    """WAF decision result."""
    action: WAFAction
    threat_score: float
    threat_type: str
    findings: list
    should_block: bool
    response_code: int
    response_body: Dict[str, Any]
    analysis_time_ms: float
    cache_hit: bool = False


class WAFEngine:
    """Core WAF engine for request analysis and blocking decisions."""
    
    def __init__(self, config: Optional[WAFConfig] = None, db_session=None):
        """Initialize WAF engine.
        
        Args:
            config: WAF configuration
            db_session: Database session for incident logging
        """
        self.config = config or WAFConfig()
        self.db_session = db_session
        
        # Initialize incident service if DB available
        self.incident_service = None
        if db_session:
            self.incident_service = IncidentService(
                db_session,
                static_analysis_enabled=1 if config.analysis.static_enabled else 0,
                dynamic_analysis_enabled=0 if config.analysis.ml_async else 1
            )
        
        # Request cache for performance
        self.cache: Dict[str, Tuple[WAFDecision, float]] = {}
        
        # Statistics
        self.stats = {
            "total_requests": 0,
            "blocked_requests": 0,
            "allowed_requests": 0,
            "challenged_requests": 0,
            "cache_hits": 0,
            "avg_analysis_time_ms": 0.0
        }
    
    async def analyze_request(
        self,
        method: str,
        path: str,
        headers: Dict[str, str],
        body: Optional[Any] = None,
        query_params: Optional[Dict[str, str]] = None,
        client_ip: Optional[str] = None
    ) -> WAFDecision:
        """Analyze a request and return blocking decision.
        
        This is the main entry point for WAF analysis.
        
        Args:
            method: HTTP method
            path: Request path
            headers: Request headers
            body: Request body
            query_params: Query parameters
            client_ip: Client IP address
            
        Returns:
            WAFDecision with action to take
        """
        start_time = time.time()
        self.stats["total_requests"] += 1
        
        # Check if path is excluded
        if self.config.is_path_excluded(path):
            return WAFDecision(
                action=WAFAction.ALLOW,
                threat_score=0.0,
                threat_type="safe",
                findings=["Path excluded from WAF"],
                should_block=False,
                response_code=200,
                response_body={},
                analysis_time_ms=0.0
            )
        
        # Check cache
        cache_key = self._generate_cache_key(method, path, headers, body, query_params)
        if self.config.analysis.cache_enabled:
            cached_decision = self._get_from_cache(cache_key)
            if cached_decision:
                self.stats["cache_hits"] += 1
                cached_decision.cache_hit = True
                return cached_decision
        
        # Check IP blacklist/whitelist
        if client_ip:
            ip_action = self._check_ip_lists(client_ip)
            if ip_action == WAFAction.BLOCK:
                return self._create_block_decision(
                    threat_score=1.0,
                    threat_type="blacklisted_ip",
                    findings=[f"IP {client_ip} is blacklisted"],
                    analysis_time_ms=(time.time() - start_time) * 1000
                )
            elif ip_action == WAFAction.ALLOW:
                return self._create_allow_decision(
                    findings=[f"IP {client_ip} is whitelisted"],
                    analysis_time_ms=(time.time() - start_time) * 1000
                )
        
        # Fast-path static analysis (synchronous for speed)
        if self.config.analysis.static_enabled:
            static_result = await self._fast_static_analysis(
                method, path, headers, body, query_params, client_ip
            )
            
            # If high confidence threat, block immediately
            if static_result["threat_score"] >= self.config.thresholds.block:
                decision = self._create_decision_from_analysis(
                    static_result,
                    analysis_time_ms=(time.time() - start_time) * 1000
                )
                
                # Cache decision
                if self.config.analysis.cache_enabled:
                    self._add_to_cache(cache_key, decision)
                
                # Log incident asynchronously
                if self.incident_service:
                    asyncio.create_task(self._log_incident(
                        method, path, headers, body, query_params, client_ip, static_result
                    ))
                
                return decision
        
        # ML analysis (async if enabled for performance)
        if self.config.analysis.ml_enabled:
            if self.config.analysis.ml_async:
                # Return fast decision, analyze with ML in background
                decision = self._create_decision_from_analysis(
                    static_result if self.config.analysis.static_enabled else {"threat_score": 0.0, "threat_type": "unknown", "findings": []},
                    analysis_time_ms=(time.time() - start_time) * 1000
                )
                
                # Run ML analysis in background
                asyncio.create_task(self._async_ml_analysis(
                    method, path, headers, body, query_params, client_ip
                ))
                
                return decision
            else:
                # Synchronous ML analysis (slower but more accurate)
                ml_result = await self._ml_analysis(
                    method, path, headers, body, query_params, client_ip
                )
                
                decision = self._create_decision_from_analysis(
                    ml_result,
                    analysis_time_ms=(time.time() - start_time) * 1000
                )
                
                # Cache decision
                if self.config.analysis.cache_enabled:
                    self._add_to_cache(cache_key, decision)
                
                return decision
        
        # Default allow if no analysis enabled
        return self._create_allow_decision(
            findings=["No analysis configured"],
            analysis_time_ms=(time.time() - start_time) * 1000
        )
    
    async def _fast_static_analysis(
        self,
        method: str,
        path: str,
        headers: Dict[str, str],
        body: Optional[Any],
        query_params: Optional[Dict[str, str]],
        client_ip: Optional[str]
    ) -> Dict[str, Any]:
        """Perform fast static analysis using pattern matching.
        
        This is optimized for speed and runs synchronously.
        """
        if not self.incident_service:
            return {"threat_score": 0.0, "threat_type": "safe", "findings": []}
        
        # Use the basic static analysis from incident service
        url = path
        if query_params:
            query_str = "&".join([f"{k}={v}" for k, v in query_params.items()])
            url += f"?{query_str}"
        
        result = self.incident_service._perform_basic_static_analysis(
            client_ip or "unknown",
            path,
            method,
            headers,
            body,
            headers.get("user-agent")
        )
        
        return result
    
    async def _ml_analysis(
        self,
        method: str,
        path: str,
        headers: Dict[str, str],
        body: Optional[Any],
        query_params: Optional[Dict[str, str]],
        client_ip: Optional[str]
    ) -> Dict[str, Any]:
        """Perform ML-based analysis."""
        if not self.incident_service:
            return {"threat_score": 0.0, "threat_type": "safe", "findings": []}
        
        url = path
        if query_params:
            query_str = "&".join([f"{k}={v}" for k, v in query_params.items()])
            url += f"?{query_str}"
        
        result = await self.incident_service.analyze_raw_request(
            method=method,
            url=url,
            path=path,
            headers=headers,
            body=body,
            query_params=query_params,
            client_ip=client_ip,
            timestamp=datetime.utcnow()
        )
        
        return result
    
    async def _async_ml_analysis(
        self,
        method: str,
        path: str,
        headers: Dict[str, str],
        body: Optional[Any],
        query_params: Optional[Dict[str, str]],
        client_ip: Optional[str]
    ) -> None:
        """Run ML analysis asynchronously in background."""
        try:
            await self._ml_analysis(method, path, headers, body, query_params, client_ip)
        except Exception as e:
            logger.error(f"Async ML analysis failed: {str(e)}")
    
    async def _log_incident(
        self,
        method: str,
        path: str,
        headers: Dict[str, str],
        body: Optional[Any],
        query_params: Optional[Dict[str, str]],
        client_ip: Optional[str],
        analysis_result: Dict[str, Any]
    ) -> None:
        """Log security incident asynchronously."""
        if not self.incident_service:
            return
        
        try:
            if analysis_result["threat_score"] >= self.config.thresholds.log:
                # This will create incident and malicious request records
                url = path
                if query_params:
                    query_str = "&".join([f"{k}={v}" for k, v in query_params.items()])
                    url += f"?{query_str}"
                
                await self.incident_service.analyze_raw_request(
                    method=method,
                    url=url,
                    path=path,
                    headers=headers,
                    body=body,
                    query_params=query_params,
                    client_ip=client_ip,
                    timestamp=datetime.utcnow()
                )
        except Exception as e:
            logger.error(f"Failed to log incident: {str(e)}")
    
    def _check_ip_lists(self, ip: str) -> Optional[WAFAction]:
        """Check if IP is in whitelist or blacklist.
        
        Returns:
            WAFAction if IP is in a list, None otherwise
        """
        if ip in self.config.ip_config.whitelist:
            return WAFAction.ALLOW
        if ip in self.config.ip_config.blacklist:
            return WAFAction.BLOCK
        return None
    
    def _generate_cache_key(
        self,
        method: str,
        path: str,
        headers: Dict[str, str],
        body: Optional[Any],
        query_params: Optional[Dict[str, str]]
    ) -> str:
        """Generate cache key for request."""
        # Create unique key based on request characteristics
        key_parts = [
            method,
            path,
            str(query_params or {}),
            str(body or "")
        ]
        key_string = "|".join(key_parts)
        return hashlib.md5(key_string.encode()).hexdigest()
    
    def _get_from_cache(self, cache_key: str) -> Optional[WAFDecision]:
        """Get decision from cache if not expired."""
        if cache_key in self.cache:
            decision, timestamp = self.cache[cache_key]
            if time.time() - timestamp < self.config.analysis.cache_ttl:
                return decision
            else:
                del self.cache[cache_key]
        return None
    
    def _add_to_cache(self, cache_key: str, decision: WAFDecision) -> None:
        """Add decision to cache."""
        self.cache[cache_key] = (decision, time.time())
        
        # Simple cache cleanup (remove old entries if cache too large)
        if len(self.cache) > 10000:
            # Remove oldest 20%
            sorted_items = sorted(self.cache.items(), key=lambda x: x[1][1])
            for key, _ in sorted_items[:2000]:
                del self.cache[key]
    
    def _create_decision_from_analysis(
        self,
        analysis_result: Dict[str, Any],
        analysis_time_ms: float
    ) -> WAFDecision:
        """Create WAF decision from analysis result."""
        threat_score = analysis_result.get("threat_score", 0.0)
        action = self.config.get_action_for_score(threat_score)
        
        if action == WAFAction.BLOCK:
            return self._create_block_decision(
                threat_score=threat_score,
                threat_type=analysis_result.get("threat_type", "unknown"),
                findings=analysis_result.get("findings", []),
                analysis_time_ms=analysis_time_ms
            )
        elif action == WAFAction.CHALLENGE:
            return self._create_challenge_decision(
                threat_score=threat_score,
                threat_type=analysis_result.get("threat_type", "suspicious"),
                findings=analysis_result.get("findings", []),
                analysis_time_ms=analysis_time_ms
            )
        else:
            return self._create_allow_decision(
                findings=analysis_result.get("findings", []),
                analysis_time_ms=analysis_time_ms
            )
    
    def _create_block_decision(
        self,
        threat_score: float,
        threat_type: str,
        findings: list,
        analysis_time_ms: float
    ) -> WAFDecision:
        """Create block decision."""
        self.stats["blocked_requests"] += 1
        
        return WAFDecision(
            action=WAFAction.BLOCK,
            threat_score=threat_score,
            threat_type=threat_type,
            findings=findings,
            should_block=True,
            response_code=403,
            response_body={
                "error": "Forbidden",
                "message": "Request blocked by WAF",
                "threat_type": threat_type,
                "request_id": self._generate_request_id()
            },
            analysis_time_ms=analysis_time_ms
        )
    
    def _create_challenge_decision(
        self,
        threat_score: float,
        threat_type: str,
        findings: list,
        analysis_time_ms: float
    ) -> WAFDecision:
        """Create challenge decision (CAPTCHA, etc)."""
        self.stats["challenged_requests"] += 1
        
        return WAFDecision(
            action=WAFAction.CHALLENGE,
            threat_score=threat_score,
            threat_type=threat_type,
            findings=findings,
            should_block=False,  # Challenges don't block, they redirect
            response_code=429,
            response_body={
                "error": "Too Many Requests",
                "message": "Please complete the security challenge",
                "challenge_url": "/challenge",
                "request_id": self._generate_request_id()
            },
            analysis_time_ms=analysis_time_ms
        )
    
    def _create_allow_decision(
        self,
        findings: list,
        analysis_time_ms: float
    ) -> WAFDecision:
        """Create allow decision."""
        self.stats["allowed_requests"] += 1
        
        return WAFDecision(
            action=WAFAction.ALLOW,
            threat_score=0.0,
            threat_type="safe",
            findings=findings,
            should_block=False,
            response_code=200,
            response_body={},
            analysis_time_ms=analysis_time_ms
        )
    
    def _generate_request_id(self) -> str:
        """Generate unique request ID."""
        return hashlib.sha256(f"{time.time()}".encode()).hexdigest()[:16]
    
    def get_stats(self) -> Dict[str, Any]:
        """Get WAF statistics."""
        return self.stats.copy()

