"""Incident management service.

This module provides functionality for managing security incidents and analyzing requests.
"""

from typing import List, Optional, Dict, Any, Tuple, Set
from datetime import datetime, timedelta
import uuid
import re
from sqlalchemy.orm import Session
from sqlalchemy import desc, or_
from fastapi import HTTPException, status
import json
from urllib.parse import unquote
import socket
import ipaddress
import humanize
from sqlalchemy.sql import func
import numpy as np
import os
import sys

# Try to import absolution package, with fallback
try:
    from absolution.model_loader import ModelLoader
    ABSOLUTION_AVAILABLE = True
    print("[INFO] Absolution package imported successfully")
except ImportError as e:
    print(f"[WARNING] Absolution package not available: {e}")
    ABSOLUTION_AVAILABLE = False
    ModelLoader = None

from services.common.models.incident import Incident, MaliciousRequest, IncidentResponse, ResponseAction
from services.common.models.user import User, APIKey
from services.user.core.user_service import UserService
from services.notification.core.notification_service import NotificationService
from services.common.models.notification import NotificationPriority
from services.incident.core.threat_intelligence import ThreatIntelligenceService

class IncidentService:
    """Service for managing security incidents and request analysis."""

    def __init__(self, db: Session, static_analysis_enabled: int = 0, dynamic_analysis_enabled: int = 1):
        """Initialize the service.
        
        Args:
            db: Database session
            static_analysis_enabled: 1 to enable static analysis, 0 to disable
            dynamic_analysis_enabled: 1 to enable ML (dynamic) analysis, 0 to disable
        """
        self.db = db
        self.user_service = UserService(db)
        self.notification_service = NotificationService(db)
        self.threat_score = 0  # Initialize threat score
        self.static_analysis_enabled = static_analysis_enabled
        self.dynamic_analysis_enabled = dynamic_analysis_enabled
        
        # Initialize the ML model loader if available
        self.model_loader = None
        if ABSOLUTION_AVAILABLE and dynamic_analysis_enabled:
            try:
                # Use the ModelLoader with proper package paths
                from absolution.model_loader import get_model_dir
                
                binary_model_path = get_model_dir("binary-classifier")
                multi_model_path = get_model_dir("multi-classifier")
                
                self.model_loader = ModelLoader(binary_model_path, multi_model_path)
                print(f"[INFO] ML models loaded successfully from absolution package")
            except Exception as e:
                print(f"[ERROR] Failed to load ML models: {str(e)}")
                self.dynamic_analysis_enabled = 0
        else:
            if not ABSOLUTION_AVAILABLE:
                print("[INFO] Absolution package not available, disabling dynamic analysis")
                self.dynamic_analysis_enabled = 0
            elif not dynamic_analysis_enabled:
                print("[INFO] Dynamic analysis disabled by configuration")
        
        # Common patterns for threat detection
        self.suspicious_patterns = {
            'sql_injection': [
                r'(?i)(union\s+all|union\s+select|insert\s+into|delete\s+from|drop\s+table|update\s+set)\s+',
                r'(?i)(\%27|\')\s*(or|and|not)\s*(\d|true|false|null)',
                r'(?i)(sleep\(|benchmark\(|waitfor\s+delay|pg_sleep)',
                r'(?i)(select|;)\s*(%27|\'|`)',
                r'(?i)(/\*.*\*/|--|#|//)',
                r'(?i)(load_file|outfile|dumpfile)',
            ],
            'xss': [
                r'(?i)<[^>]*script.*?>',
                r'(?i)(javascript|vbscript|expression|data):\s*',
                r'(?i)on\w+\s*=',
                r'(?i)(eval|setTimeout|setInterval|Function)\s*\(',
                r'(?i)<[^>]*(alert|confirm|prompt|msgbox)\s*\(',
                r'(?i)(src|href|data|action)\s*=\s*([\'"])*\s*(javascript|data):',
            ],
            'path_traversal': [
                # Basic directory traversal
                r'(?i)\.\./',
                r'(?i)\.\.\\',
                # URL encoded variants
                r'(?i)%2e%2e%2f',
                r'(?i)%2e%2e/',
                r'(?i)%2e%2e%5c',
                r'(?i)\.\.%2f',
                r'(?i)\.\.%5c',
                # Double encoded variants
                r'(?i)%252e%252e%252f',
                r'(?i)%252e%252e%255c',
                # Mixed encoding variants
                r'(?i)%2e\.%2f',
                r'(?i)\.%2e%2f',
                r'(?i)%2e\./',
                r'(?i)\.%2e/',
                # Unicode encoded
                r'(?i)%u002e%u002e%u2215',
                r'(?i)%u002e%u002e%u2216',
                # Nested traversal
                r'(?i)\.\.//+',
                r'(?i)\.\.\\\\+',
                # Common sensitive paths
                r'(?i)/etc/passwd',
                r'(?i)/etc/shadow',
                r'(?i)/etc/hosts',
                r'(?i)/proc/self',
                r'(?i)/proc/\d+',
                r'(?i)c:\\windows\\system32',
                r'(?i)windows\\system32\\drivers\\etc',
                r'(?i)boot\.ini',
                r'(?i)system\.ini',
                # Web root escaping
                r'(?i)\.{2,}[/\\]+(www|html|htdocs|public|web)',
                # Backup/temp files
                r'(?i)\.(bak|old|backup|tmp)$',
                # Log files
                r'(?i)\.(log|logs)$',
                # Config files
                r'(?i)\.(conf|config|cfg|ini)$'
            ],
            'command_injection': [
                r'(?i)[;&|`]\s*[\w\-]+',
                r'(?i)\$\([^)]*\)',
                r'(?i)`[^`]*`',
                r'(?i)\b(ping|nc|netcat|wget|curl|bash|sh|python|perl|ruby)\b',
                r'(?i)(>|>>)\s*/[a-z]+/',
                r'(?i)\|\s*[\w\-]+',
            ],
            'nosql_injection': [
                r'(?i)\$(?:ne|eq|gt|gte|lt|lte|in|nin|all|size|exists|type|not|mod|text|slice|or|and|nor|elemMatch|where|group)',
                r'(?i){\s*\$[a-z]+\s*:',
                r'(?i)\$regex',
                r'(?i)\$where\s*:',
                r'(?i)db\.[a-z]+\.find',
                r'(?i)sleep\s*\(\s*\d+\s*\)',
            ]
        }
        # Add sensitive directories to check
        self.sensitive_dirs = {
            'unix': [
                '/etc', '/var/log', '/var/www', '/usr/local',
                '/root', '/home', '/proc', '/sys', '/boot',
                '/dev', '/opt', '/usr/bin', '/bin', '/sbin'
            ],
            'windows': [
                'c:\\', 'd:\\', 'windows\\', 'program files',
                'system32', 'boot', 'config', 'repair',
                'documents and settings', 'users', 'administrator'
            ]
        }

    async def _notify_incident_stakeholders(
        self,
        incident: Incident,
        event_type: str,
        additional_data: Optional[Dict] = None
    ) -> None:
        """Send notifications to incident stakeholders.
        
        Args:
            incident: The incident
            event_type: Type of event (created, updated, resolved, etc.)
            additional_data: Additional notification data
        """
        print(f"[DEBUG] Starting notification for incident {incident.id}, event: {event_type}")
        
        # Map incident severity to notification priority
        priority_map = {
            "low": NotificationPriority.LOW,
            "medium": NotificationPriority.MEDIUM,
            "high": NotificationPriority.HIGH,
            "critical": NotificationPriority.CRITICAL
        }
        
        # Prepare notification data
        notification_data = {
            "incident_id": incident.id,
            "severity": incident.severity,
            "status": incident.status,
            "detection_source": incident.detection_source,
            "event_type": event_type,
            **(additional_data or {})
        }
        
        # Get stakeholders (reporter, assignee, and incident responders)
        stakeholders = set()
        
        # If reporter is system, check if there's an API key user
        if incident.reporter_id == "system" and incident.threat_details and "request_context" in incident.threat_details:
            api_key_id = incident.threat_details["request_context"].get("api_key_id")
            if api_key_id:
                print(f"[DEBUG] Found API key user {api_key_id}, will notify them")
                stakeholders.add(api_key_id)
            else:
                # If no API key user, notify all admin users
                print("[DEBUG] No API key user found, notifying admin users")
                admin_users = self.db.query(User).filter(User.is_superuser == True).all()
                for admin in admin_users:
                    stakeholders.add(admin.id)
        else:
            stakeholders.add(incident.reporter_id)
        
        if incident.assigned_to:
            stakeholders.add(incident.assigned_to)
        
        for response in incident.responses:
            stakeholders.add(response.responder_id)
        
        print(f"[DEBUG] Found {len(stakeholders)} stakeholders to notify")
        
        # Send notifications to all stakeholders
        for user_id in stakeholders:
            print(f"[DEBUG] Sending notification to user {user_id}")
            try:
                await self.notification_service.create_notification(
                    user_id=user_id,
                    title=f"Incident {event_type.title()}: {incident.title}",
                    message=self._generate_incident_message(incident, event_type),
                    priority=priority_map.get(incident.severity, NotificationPriority.MEDIUM),
                    incident_id=incident.id,
                    data=notification_data
                )
                print(f"[DEBUG] Successfully sent notification to user {user_id}")
            except Exception as e:
                print(f"[ERROR] Failed to send notification to user {user_id}: {str(e)}")

    def _generate_incident_message(self, incident: Incident, event_type: str) -> str:
        """Generate a human-readable incident notification message.
        
        Args:
            incident: The incident
            event_type: Type of event
            
        Returns:
            Formatted message string
        """
        if event_type == "created":
            return (
                f"New security incident detected from {incident.detection_source}.\n"
                f"Severity: {incident.severity.upper()}\n"
                f"Description: {incident.description}"
            )
        elif event_type == "updated":
            return (
                f"Incident status updated to: {incident.status}\n"
                f"Severity: {incident.severity.upper()}\n"
                f"Latest update: {incident.resolution_notes or 'No notes provided'}"
            )
        elif event_type == "resolved":
            time_to_resolve = humanize.naturaldelta(incident.resolved_at - incident.created_at)
            return (
                f"Incident has been resolved.\n"
                f"Time to resolution: {time_to_resolve}\n"
                f"Resolution notes: {incident.resolution_notes or 'No notes provided'}"
            )
        else:
            return f"Incident {event_type}: {incident.title}"

    async def create_incident(
        self,
        title: str,
        description: str,
        severity: str,
        detection_source: str,
        reporter_id: str,
        affected_assets: Optional[List[str]] = None,
        tags: Optional[List[str]] = None,
        threat_details: Optional[Dict] = None,
        assigned_to: Optional[str] = None
    ) -> Incident:
        """Create a new security incident.
        
        Args:
            title: Incident title
            description: Incident description
            severity: Incident severity level
            detection_source: Source of detection
            reporter_id: ID of user reporting the incident
            affected_assets: List of affected assets
            tags: List of tags
            threat_details: Additional threat information
            assigned_to: ID of user assigned to incident
            
        Returns:
            Created incident
        """
        incident = Incident(
            id=str(uuid.uuid4()),
            title=title,
            description=description,
            severity=severity,
            detection_source=detection_source,
            reporter_id=reporter_id,
            affected_assets=affected_assets or [],
            tags=tags or [],
            threat_details=threat_details or {},
            assigned_to=assigned_to
        )
        
        self.db.add(incident)
        self.db.commit()
        self.db.refresh(incident)
        
        # Send notifications
        await self._notify_incident_stakeholders(incident, "created")
        
        return incident

    async def update_incident(
        self,
        incident_id: str,
        update_data: Dict[str, Any],
        notify: bool = True
    ) -> Incident:
        """Update an incident.
        
        Args:
            incident_id: Incident ID
            update_data: Data to update
            notify: Whether to send notifications
            
        Returns:
            Updated incident
        """
        incident = self.db.query(Incident).filter(Incident.id == incident_id).first()
        if not incident:
            raise HTTPException(status_code=404, detail="Incident not found")
        
        # Track if status changed to resolved
        was_resolved = False
        if "status" in update_data and update_data["status"] == "resolved":
            if incident.status != "resolved":
                was_resolved = True
                update_data["resolved_at"] = datetime.utcnow()
        
        # Update incident
        for key, value in update_data.items():
            setattr(incident, key, value)
        
        self.db.commit()
        self.db.refresh(incident)
        
        # Send notifications
        if notify:
            event_type = "resolved" if was_resolved else "updated"
            await self._notify_incident_stakeholders(incident, event_type)
        
        return incident

    def add_malicious_request(
        self,
        source_ip: str,
        request_path: str,
        request_method: str,
        threat_type: str,
        threat_score: float,
        headers: Optional[Dict[str, str]] = None,
        body: Optional[Dict[str, Any]] = None,
        user_agent: Optional[str] = None,
        threat_details: Optional[Dict[str, Any]] = None
    ) -> MaliciousRequest:
        """Record a malicious request.
        
        Args:
            source_ip: Source IP address
            request_path: Request path/endpoint
            request_method: HTTP method
            threat_type: Type of threat detected
            threat_score: Threat score (0-100)
            headers: Request headers
            body: Request body
            user_agent: User agent string
            threat_details: Detailed threat information
            
        Returns:
            Created malicious request record
        """
        malicious_request = MaliciousRequest(
            id=str(uuid.uuid4()),
            source_ip=source_ip,
            request_path=request_path,
            request_method=request_method,
            threat_type=threat_type,
            threat_score=threat_score,
            headers=headers,
            body=body,
            user_agent=user_agent,
            is_blocked=threat_score >= 75,
            threat_details=threat_details
        )
        
        self.db.add(malicious_request)
        self.db.commit()
        self.db.refresh(malicious_request)
        
        return malicious_request

    def get_incident(self, incident_id: str) -> Optional[Incident]:
        """Get an incident by ID.
        
        Args:
            incident_id: Incident ID
            
        Returns:
            Incident if found, None otherwise
        """
        return self.db.query(Incident).get(incident_id)

    def list_incidents(
        self,
        page: int,
        page_size: int,
        status: Optional[str] = None,
        severity: Optional[str] = None,
        tag: Optional[str] = None,
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """List incidents with filtering and pagination."""
        query = self.db.query(Incident)

        # Apply filters
        if status:
            query = query.filter(Incident.status == status)
        if severity:
            query = query.filter(Incident.severity == severity)
        if tag:
            query = query.filter(Incident.tags.contains([tag]))
        if user_id:
            # Filter incidents where user is either reporter or assignee
            query = query.filter(
                or_(
                    Incident.reporter_id == user_id,
                    Incident.assigned_to == user_id
                )
            )

        # Get total count
        total = query.count()

        # Apply pagination
        incidents = query.offset((page - 1) * page_size).limit(page_size).all()

        return {
            "total": total,
            "items": incidents,
            "page": page,
            "page_size": page_size
        }

    async def analyze_request(
        self,
        source_ip: str,
        request_path: str,
        request_method: str,
        headers: Optional[Dict[str, str]] = None,
        body: Optional[Dict[str, Any]] = None,
        user_agent: Optional[str] = None
    ) -> Dict[str, Any]:
        """Analyze a request for security threats with enhanced threat intelligence.
        
        Args:
            source_ip: Source IP address
            request_path: Request path/endpoint
            request_method: HTTP method
            headers: Request headers
            body: Request body
            user_agent: User agent string
            
        Returns:
            Dict containing enhanced threat analysis results
        """
        # Perform existing static analysis
        static_analysis = self._perform_basic_static_analysis(
            source_ip, request_path, request_method, headers, body, user_agent
        )
        
        # Perform threat intelligence analysis
        threat_intel_analysis = await self._perform_threat_intelligence_analysis(
            source_ip, request_path, request_method, headers, body, user_agent
        )
        
        # Combine results
        combined_analysis = self._combine_analysis_results(
            static_analysis, threat_intel_analysis
        )
        
        return combined_analysis
    
    def _perform_basic_static_analysis(
        self,
        source_ip: str,
        request_path: str,
        request_method: str,
        headers: Optional[Dict[str, str]] = None,
        body: Optional[Dict[str, Any]] = None,
        user_agent: Optional[str] = None
    ) -> Dict[str, Any]:
        """Perform comprehensive static analysis for attack detection."""
        threat_score = 0
        findings = []
        threat_type = "safe"
        
        # Convert all inputs to strings for pattern matching
        path_str = str(request_path).lower()
        body_str = str(body).lower() if body else ""
        headers_str = str(headers).lower() if headers else ""
        user_agent_str = str(user_agent).lower() if user_agent else ""
        
        # Combine all inputs for comprehensive analysis
        combined_input = f"{path_str} {body_str} {headers_str} {user_agent_str}"
        
        # SQL Injection Detection
        sql_patterns = [
            r"(\'|\")\s*(or|and|not)\s*(\d|true|false|null)",
            r"union\s+(all\s+)?select",
            r"insert\s+into",
            r"delete\s+from",
            r"drop\s+table",
            r"update\s+set",
            r"(\'|\")\s*;\s*",
            r"(\'|\")\s*--\s*",
            r"(\'|\")\s*#\s*",
            r"(\'|\")\s*/\*",
            r"(\'|\")\s*or\s*1\s*=\s*1",
            r"(\'|\")\s*or\s*true",
            r"(\'|\")\s*or\s*false",
            r"(\'|\")\s*and\s*1\s*=\s*1",
            r"(\'|\")\s*and\s*true"
        ]
        
        for pattern in sql_patterns:
            if re.search(pattern, combined_input, re.IGNORECASE):
                threat_score += 85
                findings.append(f"SQL injection pattern detected: {pattern}")
                threat_type = "sql_injection"
                break
        
        # XSS Detection
        xss_patterns = [
            r"<script[^>]*>",
            r"javascript:",
            r"vbscript:",
            r"on\w+\s*=",
            r"eval\s*\(",
            r"setTimeout\s*\(",
            r"setInterval\s*\(",
            r"alert\s*\(",
            r"confirm\s*\(",
            r"prompt\s*\(",
            r"<iframe[^>]*>",
            r"<object[^>]*>",
            r"<embed[^>]*>",
            r"<link[^>]*javascript:",
            r"<img[^>]*onerror="
        ]
        
        for pattern in xss_patterns:
            if re.search(pattern, combined_input, re.IGNORECASE):
                threat_score += 80
                findings.append(f"XSS pattern detected: {pattern}")
                threat_type = "xss"
                break
        
        # Command Injection Detection
        cmd_patterns = [
            r"[;&|`]\s*[\w\-]+",
            r"\$\([^)]*\)",
            r"`[^`]*`",
            r"\b(ping|nc|netcat|wget|curl|bash|sh|python|perl|ruby)\b",
            r">\s*/[a-z]+/",
            r"\|\s*[\w\-]+",
            r"&&\s*[\w\-]+",
            r"\|\|\s*[\w\-]+"
        ]
        
        for pattern in cmd_patterns:
            if re.search(pattern, combined_input, re.IGNORECASE):
                threat_score += 90
                findings.append(f"Command injection pattern detected: {pattern}")
                threat_type = "command_injection"
                break
        
        # Path Traversal Detection
        path_patterns = [
            r"\.\./",
            r"\.\.\\",
            r"%2e%2e%2f",
            r"%2e%2e/",
            r"%2e%2e%5c",
            r"\.\.%2f",
            r"\.\.%5c",
            r"%252e%252e%252f",
            r"%252e%252e%255c",
            r"/etc/passwd",
            r"/etc/shadow",
            r"/etc/hosts",
            r"c:\\windows\\system32",
            r"windows\\system32\\drivers\\etc"
        ]
        
        for pattern in path_patterns:
            if re.search(pattern, combined_input, re.IGNORECASE):
                threat_score += 85
                findings.append(f"Path traversal pattern detected: {pattern}")
                threat_type = "path_traversal"
                break
        
        # NoSQL Injection Detection
        nosql_patterns = [
            r"\$\w+\s*:",
            r"\$ne\s*:",
            r"\$eq\s*:",
            r"\$gt\s*:",
            r"\$gte\s*:",
            r"\$lt\s*:",
            r"\$lte\s*:",
            r"\$in\s*:",
            r"\$nin\s*:",
            r"\$all\s*:",
            r"\$size\s*:",
            r"\$exists\s*:",
            r"\$type\s*:",
            r"\$not\s*:",
            r"\$mod\s*:",
            r"\$text\s*:",
            r"\$slice\s*:",
            r"\$or\s*:",
            r"\$and\s*:",
            r"\$nor\s*:",
            r"\$where\s*:",
            r"\$regex\s*:"
        ]
        
        for pattern in nosql_patterns:
            if re.search(pattern, combined_input, re.IGNORECASE):
                threat_score += 80
                findings.append(f"NoSQL injection pattern detected: {pattern}")
                threat_type = "nosql_injection"
                break
        
        # Suspicious Headers Detection
        if headers:
            if "X-Forwarded-For" in headers:
                threat_score += 10
                findings.append("Suspicious proxy usage detected")
            
            # Check for suspicious user agents
            user_agent = headers.get("user-agent", "").lower()
            suspicious_agents = [
                "curl", "python-requests", "wget", "nmap", "masscan", 
                "sqlmap", "nikto", "zap", "burp", "acunetix"
            ]
            if any(agent in user_agent for agent in suspicious_agents):
                threat_score += 20
                findings.append(f"Suspicious user agent detected: {user_agent}")
        
        # Admin Access Attempts
        if "admin" in path_str:
            threat_score += 20
            findings.append("Attempted admin access")
            threat_type = "suspicious"
        
        # Normalize threat score to 0-1 range
        normalized_score = min(threat_score, 100) / 100.0
        
        # Determine if should block (lower threshold for better security)
        should_block = normalized_score >= 0.5  # Changed from 0.75 to 0.5
        
        return {
            "threat_score": normalized_score,
            "threat_type": self._validate_threat_type(threat_type if threat_score > 0 else "safe"),
            "findings": findings,
            "should_block": should_block,
            "analysis_type": "static"
        }
    
    async def _perform_threat_intelligence_analysis(
        self,
        source_ip: str,
        request_path: str,
        request_method: str,
        headers: Optional[Dict[str, str]] = None,
        body: Optional[Dict[str, Any]] = None,
        user_agent: Optional[str] = None
    ) -> Dict[str, Any]:
        """Perform threat intelligence analysis."""
        try:
            # Create ThreatIntelligenceService instance directly (no async context manager)
            ti_service = ThreatIntelligenceService()
            
            # Extract domain from headers or path
            domain = None
            if headers and "host" in headers:
                domain = headers["host"].split(":")[0]
            
            # Extract URL from request
            url = f"http://{domain}{request_path}" if domain else request_path
            
            # Get comprehensive threat analysis
            threat_analysis = await ti_service.comprehensive_threat_analysis(
                method=request_method,
                url=url,
                path=request_path,
                headers=headers or {},
                body=body,
                query_params=None,
                client_ip=source_ip
            )
            
            return {
                "threat_score": threat_analysis["overall_threat_score"] / 100.0,  # Normalize to 0-1
                "threat_type": self._validate_threat_type("suspicious" if threat_analysis.get("overall_threat_score", 0) > 50 else "safe"),
                "findings": threat_analysis.get("recommendations", []),
                "should_block": threat_analysis.get("overall_threat_score", 0) >= 75,
                "analysis_type": "threat_intelligence",
                "threat_indicators": threat_analysis.get("threat_indicators", []),
                "confidence": 0.5  # Default confidence
            }
            
        except Exception as e:
            print(f"[ERROR] Threat intelligence analysis failed: {str(e)}")
            return {
                "threat_score": 0.0,
                "threat_type": "safe",
                "findings": ["Threat intelligence analysis failed"],
                "should_block": False,
                "analysis_type": "threat_intelligence",
                "error": str(e)
            }
    
    def _format_request_content(
        self,
        method: str,
        path: str,
        headers: Optional[Dict[str, str]] = None,
        body: Optional[Dict[str, Any]] = None,
        user_agent: Optional[str] = None
    ) -> str:
        """Format request content for YARA analysis."""
        content_parts = [
            f"{method} {path}",
            f"User-Agent: {user_agent}" if user_agent else "",
        ]
        
        if headers:
            for key, value in headers.items():
                content_parts.append(f"{key}: {value}")
        
        if body:
            content_parts.append(str(body))
        
        return "\n".join(content_parts)
    
    def _combine_analysis_results(
        self,
        static_analysis: Dict[str, Any],
        threat_intel_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Combine static and threat intelligence analysis results."""
        # Take the higher threat score (both should already be normalized 0-1)
        combined_threat_score = max(
            static_analysis["threat_score"],
            threat_intel_analysis["threat_score"]
        )
        
        # Combine findings
        combined_findings = static_analysis["findings"] + threat_intel_analysis["findings"]
        
        # Determine threat type
        if threat_intel_analysis["threat_score"] > static_analysis["threat_score"]:
            threat_type = threat_intel_analysis["threat_type"]
        else:
            threat_type = static_analysis["threat_type"]
        
        # Determine if should block (use normalized score)
        should_block = combined_threat_score >= 0.5  # Changed from 0.75 to 0.5
        
        return {
            "threat_score": combined_threat_score,
            "threat_type": self._validate_threat_type(threat_type),
            "findings": combined_findings,
            "should_block": should_block,
            "analysis_methods": ["static", "threat_intelligence"],
            "static_analysis": static_analysis,
            "threat_intelligence_analysis": threat_intel_analysis,
            "confidence": threat_intel_analysis.get("confidence", 0.0),
            "recommendations": threat_intel_analysis.get("findings", [])
        }

    def _create_detailed_threat_analysis(
        self,
        path: str,
        url: str,
        method: str,
        headers: Dict[str, str],
        body: Optional[Dict[str, Any]],
        query_params: Optional[Dict[str, str]],
        client_ip: str,
        findings: List[str],
        threat_types: Set[str],
        pattern_matches: Dict[str, List[Dict[str, Any]]],
        api_key_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create detailed threat analysis for storage."""
        return {
            "request_context": {
                "timestamp": datetime.utcnow().isoformat(),
                "method": method,
                "url": url,
                "path": path,
                "headers": headers,
                "body": body,
                "query_params": query_params,
                "client_info": self._get_client_info(client_ip, headers),
                "api_key_id": api_key_id
            },
            "threat_analysis": {
                "overall_score": self.threat_score,
                "normalized_score": min(self.threat_score, 100) / 100.0,
                "threat_types": list(threat_types),
                "primary_threat": self._determine_primary_threat(threat_types, self.threat_score / 100.0),
                "findings": findings,
                "pattern_matches": pattern_matches,
                "attack_vectors": self._analyze_attack_vectors(pattern_matches)
            },
            "detection_timeline": {
                "start_time": datetime.utcnow().isoformat(),
                "steps": self._get_detection_steps(findings, pattern_matches),
                "end_time": datetime.utcnow().isoformat()
            },
            "risk_assessment": self._assess_risk(threat_types, self.threat_score)
        }

    def _get_client_info(self, client_ip: str, headers: Dict[str, str]) -> Dict[str, Any]:
        """Get detailed client information."""
        info = {
            "ip": client_ip,
            "user_agent": headers.get("user-agent", "unknown"),
            "forwarded_for": headers.get("x-forwarded-for", ""),
            "platform": self._detect_platform(headers.get("user-agent", "")),
            "is_proxy": bool(headers.get("x-forwarded-for")),
        }
        
        try:
            hostname = socket.gethostbyaddr(client_ip)[0]
            info["hostname"] = hostname
        except:
            info["hostname"] = "unknown"
            
        try:
            ip_obj = ipaddress.ip_address(client_ip)
            info["ip_version"] = "IPv6" if ip_obj.version == 6 else "IPv4"
            info["is_private"] = ip_obj.is_private
        except:
            info["ip_version"] = "unknown"
            info["is_private"] = False
            
        return info

    def _detect_platform(self, user_agent: str) -> str:
        """Detect client platform from user agent."""
        ua = user_agent.lower()
        if "windows" in ua:
            return "Windows"
        elif "android" in ua:
            return "Android"
        elif "iphone" in ua or "ipad" in ua:
            return "iOS"
        elif "mac" in ua:
            return "MacOS"
        elif "linux" in ua:
            return "Linux"
        return "Unknown"

    def _analyze_attack_vectors(self, pattern_matches: Dict[str, List[Dict[str, Any]]]) -> Dict[str, Any]:
        """Analyze attack vectors from pattern matches."""
        vectors = {
            "input_points": set(),
            "techniques": set(),
            "severity_distribution": {"high": 0, "medium": 0, "low": 0},
            "pattern_frequency": {}
        }
        
        for attack_type, matches in pattern_matches.items():
            vectors["techniques"].add(attack_type)
            vectors["pattern_frequency"][attack_type] = len(matches)
            
            for match in matches:
                vectors["input_points"].add(match.get("location", "unknown"))
                severity = match.get("severity", "medium")
                vectors["severity_distribution"][severity] += 1
                
        # Convert sets to lists for JSON serialization
        vectors["input_points"] = list(vectors["input_points"])
        vectors["techniques"] = list(vectors["techniques"])
        
        return vectors

    def _assess_risk(self, threat_types: Set[str], threat_score: float) -> Dict[str, Any]:
        """Assess risk level and provide detailed risk analysis."""
        risk_levels = {
            "critical": {"min_score": 90, "weight": 5},
            "high": {"min_score": 75, "weight": 4},
            "medium": {"min_score": 50, "weight": 3},
            "low": {"min_score": 25, "weight": 2},
            "info": {"min_score": 0, "weight": 1}
        }
        
        # Determine base risk level from threat score
        risk_level = "info"
        for level, criteria in risk_levels.items():
            if threat_score >= criteria["min_score"]:
                risk_level = level
                break
                
        # Calculate risk factors
        risk_factors = []
        if "command_injection" in threat_types:
            risk_factors.append({"factor": "Command injection potential", "weight": 5})
        if "sql_injection" in threat_types:
            risk_factors.append({"factor": "SQL injection potential", "weight": 4})
        if "path_traversal" in threat_types:
            risk_factors.append({"factor": "File system access potential", "weight": 4})
            
        return {
            "level": risk_level,
            "score": threat_score,
            "factors": risk_factors,
            "potential_impact": self._assess_potential_impact(threat_types),
            "mitigation_priority": "immediate" if threat_score >= 75 else "high" if threat_score >= 50 else "normal"
        }

    def _assess_potential_impact(self, threat_types: Set[str]) -> Dict[str, Any]:
        """Assess potential impact of detected threats."""
        impact = {
            "confidentiality": 0,
            "integrity": 0,
            "availability": 0,
            "affected_systems": []
        }
        
        impact_mapping = {
            "sql_injection": {
                "confidentiality": 8,
                "integrity": 9,
                "systems": ["database", "data storage"]
            },
            "command_injection": {
                "confidentiality": 9,
                "integrity": 9,
                "availability": 9,
                "systems": ["operating system", "application server"]
            },
            "path_traversal": {
                "confidentiality": 7,
                "integrity": 6,
                "systems": ["file system", "configuration"]
            },
            "xss": {
                "confidentiality": 6,
                "integrity": 5,
                "availability": 4,
                "systems": ["client browser", "user session"]
            }
        }
        
        for threat_type in threat_types:
            if threat_type in impact_mapping:
                impact_data = impact_mapping[threat_type]
                impact["confidentiality"] = max(impact["confidentiality"], impact_data.get("confidentiality", 0))
                impact["integrity"] = max(impact["integrity"], impact_data.get("integrity", 0))
                impact["availability"] = max(impact["availability"], impact_data.get("availability", 0))
                impact["affected_systems"].extend(impact_data.get("systems", []))
                
        impact["affected_systems"] = list(set(impact["affected_systems"]))
        return impact

    def _get_detection_steps(
        self,
        findings: List[str],
        pattern_matches: Dict[str, List[Dict[str, Any]]]
    ) -> List[Dict[str, Any]]:
        """Create timeline of detection steps."""
        steps = []
        current_time = datetime.utcnow()
        
        # Initial request analysis
        steps.append({
            "timestamp": current_time.isoformat(),
            "phase": "initial_analysis",
            "action": "Request received for analysis",
            "details": "Starting security analysis of incoming request"
        })
        
        # Pattern matching steps
        for attack_type, matches in pattern_matches.items():
            if matches:
                steps.append({
                    "timestamp": current_time.isoformat(),
                    "phase": "pattern_matching",
                    "action": f"Detected {attack_type} patterns",
                    "details": {
                        "pattern_count": len(matches),
                        "locations": [m.get("location") for m in matches],
                        "severity": max(m.get("severity", "medium") for m in matches)
                    }
                })
                
        # Findings documentation
        for finding in findings:
            steps.append({
                "timestamp": current_time.isoformat(),
                "phase": "threat_identification",
                "action": "Documented security finding",
                "details": finding
            })
            
        return steps

    async def analyze_raw_request(
        self,
        method: str,
        url: str,
        path: str,
        headers: Dict[str, str],
        body: Optional[Any] = None,
        query_params: Optional[Dict[str, str]] = None,
        client_ip: Optional[str] = None,
        api_key_id: Optional[str] = None,
        timestamp: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Analyze a raw request for security threats using static and/or ML-based analysis based on flags."""
        print(f"[DEBUG] Starting request analysis for path: {path}")
        self.threat_score = 0
        findings = []
        threat_types = set()
        pattern_matches = {
            "sql_injection": [],
            "xss": [],
            "path_traversal": [],
            "command_injection": [],
            "nosql_injection": []
        }

        static_analysis_result = None
        ml_analysis_result = None

        # Perform static analysis if enabled
        if self.static_analysis_enabled:
            static_analysis_result = self._perform_static_analysis(
                path, url, method, headers, body, query_params, client_ip
            )
            # If static analysis detects a high-confidence threat and dynamic is disabled, return
            if not self.dynamic_analysis_enabled and static_analysis_result["threat_score"] >= 0.75:
                print("[DEBUG] High-confidence threat detected in static analysis, skipping ML analysis (flag)")
                return await self._create_analysis_result(
                    static_analysis_result, path, url, method, headers, body,
                    query_params, client_ip, api_key_id, timestamp
                )

        # Perform ML-based analysis if enabled
        if self.dynamic_analysis_enabled:
            print("[DEBUG] Performing ML-based analysis")
            ml_analysis_result = self._perform_ml_analysis(
                method, url, path, headers, body, query_params
            )
            # If static analysis is disabled, return ML result directly
            if not self.static_analysis_enabled:
                return await self._create_analysis_result(
                    ml_analysis_result, path, url, method, headers, body,
                    query_params, client_ip, api_key_id, timestamp
                )

        # If both are enabled, combine results
        if self.static_analysis_enabled and self.dynamic_analysis_enabled:
            combined_result = self._combine_analysis_results(
                static_analysis_result, ml_analysis_result
            )
            return await self._create_analysis_result(
                combined_result, path, url, method, headers, body,
                query_params, client_ip, api_key_id, timestamp
            )

        # If neither is enabled, return a default safe result
        return {
            "threat_score": 0.0,
            "threat_type": "safe",
            "findings": ["No analysis performed (both static and dynamic analysis disabled)."],
            "should_block": False,
            "incident_created": False,
            "incident_id": None,
            "threat_details": {}
        }

    def _perform_static_analysis(
        self,
        path: str,
        url: str,
        method: str,
        headers: Dict[str, str],
        body: Optional[Any],
        query_params: Optional[Dict[str, str]],
        client_ip: Optional[str]
    ) -> Dict[str, Any]:
        """Perform static analysis using pattern matching and heuristics."""
        findings = []
        threat_types = set()
        pattern_matches = {
            "sql_injection": [],
            "xss": [],
            "path_traversal": [],
            "command_injection": [],
            "nosql_injection": []
        }

        # Analyze path traversal
        path_findings, is_path_traversal, path_matches = self._analyze_path_traversal(
            path, url, query_params, body
        )
        if path_findings:
            findings.extend(path_findings)
            if is_path_traversal:
                threat_types.add("path_traversal")
                pattern_matches["path_traversal"].extend(path_matches)

        # Analyze all inputs
        path_str = str(path).lower()
        body_str = str(body).lower() if body else ""
        query_str = str(query_params).lower() if query_params else ""
        combined_input = f"{path_str} {body_str} {query_str}"

        # Check each attack type
        for attack_type, patterns in self.suspicious_patterns.items():
            if attack_type == "path_traversal":
                continue  # Already handled above
                
            for pattern in patterns:
                matches = re.finditer(pattern, combined_input)
                for match in matches:
                    match_data = {
                        "pattern": pattern,
                        "matched_text": match.group(),
                        "location": self._determine_match_location(
                            match.group(), path_str, body_str, query_str
                        ),
                        "severity": self._get_pattern_severity(attack_type, pattern),
                        "context": self._get_match_context(combined_input, match)
                    }
                    pattern_matches[attack_type].append(match_data)
                    
                    if attack_type not in threat_types:
                        threat_types.add(attack_type)
                        findings.append(f"{attack_type.replace('_', ' ').title()} attempt detected")
                        self.threat_score += self._get_attack_type_score(attack_type)

        # Analyze headers
        header_findings, header_matches = self._analyze_headers(headers)
        if header_findings:
            findings.extend(header_findings)
            for attack_type, matches in header_matches.items():
                pattern_matches[attack_type].extend(matches)

        return {
            "threat_score": min(self.threat_score, 100) / 100.0,
            "threat_type": self._validate_threat_type(self._determine_primary_threat(threat_types, self.threat_score / 100.0)),
            "findings": findings,
            "pattern_matches": pattern_matches,
            "threat_types": threat_types
        }

    def _validate_threat_type(self, threat_type: str) -> str:
        """Validate and normalize threat type to ensure it matches the ThreatType enum.
        
        Args:
            threat_type: Raw threat type string
            
        Returns:
            Validated threat type that matches the enum
        """
        # Valid threat types from the enum
        valid_types = {
            "sql_injection", "xss", "command_injection", "path_traversal", 
            "nosql_injection", "safe", "suspicious", "benign", "deserialization",
            "graphql_attacks", "jwt_attacks", "lfi", "modern_cmdi", 
            "modern_file_attacks", "modern_sqli", "modern_ssrf", "modern_xss",
            "open_redirect", "prototype_pollution", "sqli", "ssrf", 
            "template_injection", "xxe_injection"
        }
        
        # Normalize the threat type
        normalized = threat_type.lower().replace(" ", "_").replace("-", "_")
        
        # Map common variations to valid types
        type_mapping = {
            "unknown": "suspicious",
            "unauthorized_access": "suspicious", 
            "malware": "suspicious",
            "phishing": "suspicious",
            "ddos": "suspicious",
            "brute_force": "suspicious",
            "injection": "sql_injection",  # Default to SQL injection for generic injection
            "script_injection": "xss",
            "code_injection": "command_injection",
            "file_inclusion": "lfi",
            "directory_traversal": "path_traversal",
            "sql": "sql_injection",
            "nosql": "nosql_injection"
        }
        
        # Check if it's a valid type
        if normalized in valid_types:
            return normalized
        
        # Check if it can be mapped
        if normalized in type_mapping:
            return type_mapping[normalized]
        
        # Default to suspicious for unknown types
        return "suspicious"

    def _perform_ml_analysis(
        self,
        method: str,
        url: str,
        path: str,
        headers: Dict[str, str],
        body: Optional[Any],
        query_params: Optional[Dict[str, str]]
    ) -> Dict[str, Any]:
        """Perform ML-based analysis using the model loader."""
        # Check if model loader is available
        if self.model_loader is None:
            return {
                "threat_score": 0.0,
                "threat_type": "safe",
                "findings": ["ML analysis not available - models not loaded"],
                "ml_scores": {}
            }
        
        # Format request for ML analysis
        formatted_request = self._format_request_for_ml(
            method, url, path, headers, body, query_params
        )
        
        # Get ML predictions
        ml_result = self.model_loader.detect_attack(formatted_request)
        
        # Validate and normalize the threat type
        validated_threat_type = self._validate_threat_type(ml_result["final_label"])
        
        return {
            "threat_score": ml_result["confidence"],
            "threat_type": validated_threat_type,
            "findings": [f"ML model detected {validated_threat_type} with confidence {ml_result['confidence']:.2f}"],
            "ml_scores": {
                "binary": ml_result["binary_score"],
                "multi": ml_result["multi_scores"],
                "energy": ml_result["energy_score"]
            }
        }

    def _format_request_for_ml(
        self,
        method: str,
        url: str,
        path: str,
        headers: Dict[str, str],
        body: Optional[Any],
        query_params: Optional[Dict[str, str]]
    ) -> str:
        """Format request data for ML analysis as a proper HTTP request string."""
        # Build the request line
        request_line = f"{method} {path}"
        
        # Add query parameters to the path if present
        if query_params:
            query_string = "&".join([f"{k}={v}" for k, v in query_params.items()])
            request_line += f"?{query_string}"
        
        request_line += " HTTP/1.1"
        
        # Build the formatted request
        formatted = request_line + "\r\n"
        
        # Add headers
        for key, value in headers.items():
            formatted += f"{key}: {value}\r\n"
        
        # Add body if present
        if body:
            formatted += "\r\n"
            if isinstance(body, dict):
                # Convert dict to form data
                body_data = "&".join([f"{k}={v}" for k, v in body.items()])
                formatted += body_data
            else:
                formatted += str(body)
        
        return formatted

    def _combine_analysis_results(
        self,
        static_analysis_result: Dict[str, Any],
        ml_analysis_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Combine results from static and ML analysis."""
        # If static analysis found a clear threat, use its results
        if static_analysis_result["threat_score"] >= 0.75:
            return static_analysis_result
            
        # If ML analysis found a clear threat, use its results
        if ml_analysis_result["threat_score"] >= 0.75:
            return ml_analysis_result
            
        # Combine findings and take the higher threat score
        combined_findings = static_analysis_result["findings"] + ml_analysis_result["findings"]
        combined_threat_score = max(
            static_analysis_result["threat_score"],
            ml_analysis_result["threat_score"]
        )
        
        # Determine final threat type
        if combined_threat_score >= 0.5:
            threat_type = ml_analysis_result["threat_type"] if ml_analysis_result["threat_score"] > static_analysis_result["threat_score"] else static_analysis_result["threat_type"]
        else:
            threat_type = "safe"
            
        return {
            "threat_score": combined_threat_score,
            "threat_type": self._validate_threat_type(threat_type),
            "findings": combined_findings,
            "should_block": combined_threat_score >= 0.75,
            "analysis_methods": ["static", "ML"],
            "static_analysis": static_analysis_result,
            "ml_analysis": ml_analysis_result,
            "confidence": ml_analysis_result.get("confidence", 0.0),
            "recommendations": ml_analysis_result.get("findings", [])
        }

    async def _create_analysis_result(
        self,
        analysis_result: Dict[str, Any],
        path: str,
        url: str,
        method: str,
        headers: Dict[str, str],
        body: Optional[Any],
        query_params: Optional[Dict[str, str]],
        client_ip: Optional[str],
        api_key_id: Optional[str],
        timestamp: Optional[datetime]
    ) -> Dict[str, Any]:
        """Create the final analysis result and handle incident creation if needed."""
        # Create comprehensive threat details
        threat_details = self._create_detailed_threat_analysis(
            path, url, method, headers, body, query_params,
            client_ip or "unknown", analysis_result["findings"],
            analysis_result.get("threat_types", set()),
            analysis_result.get("pattern_matches", {}),
            api_key_id
        )

        # Add ML scores if available
        if "ml_scores" in analysis_result:
            threat_details["ml_analysis"] = analysis_result["ml_scores"]

        # Make threat_details JSON serializable
        threat_details = self.make_json_serializable(threat_details)

        final_result = {
            "threat_score": analysis_result["threat_score"],
            "threat_type": analysis_result["threat_type"],
            "findings": analysis_result["findings"],
            "should_block": analysis_result["threat_score"] >= 0.75,
            "incident_created": False,
            "incident_id": None,
            "threat_details": threat_details
        }

        # Create malicious request record if threat detected
        if final_result["threat_score"] > 0:
            print(f"[INFO] Threat detected! Score: {final_result['threat_score']}, Type: {final_result['threat_type']}")
            
            # Get user_id from API key
            reporter_id = "system"  # Default to system
            if api_key_id:
                try:
                    api_key = self.db.query(APIKey).filter(APIKey.id == api_key_id).first()
                    if api_key and api_key.user_id:
                        reporter_id = api_key.user_id
                except Exception as e:
                    print(f"[ERROR] Failed to get user for API key {api_key_id}: {str(e)}")
            
            # Create malicious request record
            malicious_request = MaliciousRequest(
                id=str(uuid.uuid4()),
                source_ip=client_ip or headers.get("x-forwarded-for", "unknown"),
                request_path=path,
                request_method=method,
                threat_type=final_result["threat_type"],
                threat_score=final_result["threat_score"],
                headers=headers,
                body=body,
                user_agent=headers.get("user-agent"),
                timestamp=timestamp or datetime.utcnow(),
                is_blocked=final_result["should_block"],
                api_key_id=api_key_id,
                threat_details=threat_details
            )
            
            self.db.add(malicious_request)
            self.db.commit()
            self.db.refresh(malicious_request)

            # Create incident if threat score is high enough
            if final_result["threat_score"] >= 0.5:
                try:
                    incident = await self.create_incident(
                        title=f"Detected {final_result['threat_type']} Attack",
                        description=self._generate_incident_description(
                            client_ip or headers.get("x-forwarded-for", "unknown"),
                            path,
                            method,
                            final_result["threat_score"],
                            final_result["findings"]
                        ),
                        severity="high" if final_result["threat_score"] >= 0.75 else "medium",
                        detection_source="security_analysis",
                        reporter_id=reporter_id,
                        affected_assets=["web-application"],
                        tags=[final_result["threat_type"], "automated-detection"],
                        threat_details=threat_details
                    )
                    
                    malicious_request.incident_id = incident.id
                    self.db.commit()
                    
                    final_result["incident_created"] = True
                    final_result["incident_id"] = incident.id
                    
                except Exception as e:
                    print(f"[ERROR] Failed to create incident: {str(e)}")
                    self.db.rollback()

        return final_result

    def _determine_match_location(
        self,
        match_text: str,
        path_str: str,
        body_str: str,
        query_str: str
    ) -> str:
        """Determine where in the request the match was found."""
        if match_text in path_str:
            return "path"
        elif body_str and match_text in body_str:
            return "body"
        elif query_str and match_text in query_str:
            return "query_parameters"
        return "unknown"

    def _get_pattern_severity(self, attack_type: str, pattern: str) -> str:
        """Determine severity of a specific pattern match."""
        high_severity_indicators = {
            "sql_injection": ["union", "select", "drop", "delete"],
            "command_injection": ["bash", "sh", "cmd", "powershell"],
            "path_traversal": ["passwd", "shadow", "boot.ini"],
            "xss": ["script", "onerror", "onload"],
            "nosql_injection": ["$where", "$ne", "$gt"]
        }
        
        if attack_type in high_severity_indicators:
            if any(indicator in pattern.lower() for indicator in high_severity_indicators[attack_type]):
                return "high"
        return "medium"

    def _get_match_context(self, input_str: str, match: re.Match) -> Dict[str, Any]:
        """Get context around the pattern match."""
        start = max(0, match.start() - 20)
        end = min(len(input_str), match.end() + 20)
        return {
            "before": input_str[start:match.start()],
            "matched": match.group(),
            "after": input_str[match.end():end],
            "start_pos": match.start(),
            "end_pos": match.end()
        }

    def _get_attack_type_score(self, attack_type: str) -> int:
        """Get base score for attack type."""
        scores = {
            "command_injection": 90,
            "sql_injection": 80,
            "path_traversal": 85,
            "nosql_injection": 80,
            "xss": 75
        }
        return scores.get(attack_type, 70)

    def _analyze_headers(self, headers: Dict[str, str]) -> tuple[List[str], Dict[str, List[Dict[str, Any]]]]:
        """Analyze request headers for suspicious patterns."""
        findings = []
        pattern_matches = {
            "sql_injection": [],
            "xss": [],
            "path_traversal": [],
            "command_injection": [],
            "nosql_injection": []
        }
        
        # Check for suspicious user agent
        user_agent = headers.get("user-agent", "").lower()
        if not user_agent or user_agent in ["", "curl", "python-requests", "postman"]:
            findings.append("Suspicious or missing User-Agent")
            
        # Check for proxy chains
        if "x-forwarded-for" in headers:
            ips = headers["x-forwarded-for"].split(",")
            if len(ips) > 2:
                findings.append("Multiple proxy chain detected")
                
        # Check for common attack headers
        suspicious_headers = [
            "x-originally-forwarded-for",
            "x-remote-addr",
            "x-remote-ip",
            "x-remote-user"
        ]
        found_suspicious = [h for h in suspicious_headers if h in headers]
        if found_suspicious:
            findings.append(f"Suspicious headers detected: {', '.join(found_suspicious)}")
            
        return findings, pattern_matches

    def _analyze_path_traversal(
        self,
        path: str,
        url: str,
        query_params: Optional[Dict[str, str]],
        body: Optional[Dict[str, Any]]
    ) -> tuple[List[str], bool, List[Dict[str, Any]]]:
        """Dedicated method for path traversal detection.
        
        Returns:
            Tuple of (findings list, is_path_traversal boolean, path_matches list)
        """
        findings = []
        is_path_traversal = False
        path_matches = []

        # Function to check a string for path traversal
        def check_path_traversal(input_str: str, context: str = "") -> None:
            nonlocal is_path_traversal
            if not input_str:
                return

            # URL decode the input up to 2 levels to catch encoded attacks
            decoded = input_str
            try:
                decoded = unquote(unquote(input_str))
            except Exception:
                pass

            # Check for directory traversal patterns
            for pattern in self.suspicious_patterns['path_traversal']:
                if re.search(pattern, decoded):
                    is_path_traversal = True
                    finding = f"Path traversal attempt detected{' in ' + context if context else ''}"
                    if finding not in findings:
                        findings.append(finding)
                    self.threat_score += 85
                    break

            # Check for sensitive directory access
            for os_type, dirs in self.sensitive_dirs.items():
                for dir in dirs:
                    if dir.lower() in decoded.lower():
                        is_path_traversal = True
                        findings.append(f"Attempted access to sensitive {os_type} directory: {dir}")
                        self.threat_score += 85
                        break

            # Check for multiple levels of traversal
            if decoded.count('../') > 1 or decoded.count('..\\') > 1:
                is_path_traversal = True
                findings.append("Multiple directory traversal sequences detected")
                self.threat_score += 85

        # Check URL and path
        check_path_traversal(url, "URL")
        check_path_traversal(path, "path")

        # Check query parameters
        if query_params:
            for key, value in query_params.items():
                check_path_traversal(str(key), f"query parameter '{key}'")
                check_path_traversal(str(value), f"query parameter '{key}'")

        # Check body recursively
        def check_body_recursively(data: Any, parent_key: str = "") -> None:
            if isinstance(data, dict):
                for key, value in data.items():
                    current_key = f"{parent_key}.{key}" if parent_key else key
                    check_path_traversal(str(key), f"body field name '{current_key}'")
                    check_body_recursively(value, current_key)
            elif isinstance(data, (list, tuple)):
                for i, item in enumerate(data):
                    current_key = f"{parent_key}[{i}]" if parent_key else f"index {i}"
                    check_body_recursively(item, current_key)
            elif isinstance(data, str):
                check_path_traversal(data, f"body field '{parent_key}'")

        if body:
            check_body_recursively(body)

        return findings, is_path_traversal, path_matches

    def _generate_incident_description(
        self,
        client_ip: str,
        path: str,
        method: str,
        threat_score: float,
        findings: List[str]
    ) -> str:
        """Generate a detailed incident description."""
        return f"""Blocked suspicious request from {client_ip}
Method: {method}
Path: {path}
Threat Score: {threat_score}

Findings:
{chr(10).join('- ' + finding for finding in findings)}

This incident was automatically created based on threat detection rules.
Please review the request details and findings to determine if further action is needed."""

    def _determine_primary_threat(self, threat_types: Set[str], threat_score: float) -> str:
        """Determine the primary threat type based on severity and score.
        
        Args:
            threat_types: Set of detected threat types
            threat_score: Normalized threat score (0-1)
            
        Returns:
            Primary threat type or 'safe'/'suspicious' if no specific threats
        """
        if not threat_types:
            return "safe" if threat_score < 0.5 else "suspicious"

        # Define threat severity order
        severity_order = {
            "command_injection": 5,  # Most severe
            "sql_injection": 4,
            "path_traversal": 4,
            "nosql_injection": 3,
            "xss": 3,
            "suspicious": 1  # Least severe
        }

        # Return the threat type with highest severity
        return max(threat_types, key=lambda x: severity_order.get(x, 0))

    def get_user_analytics(self, user_id: str, time_range: str = "30d") -> Dict[str, Any]:
        """Get analytics for a specific user.
        
        Args:
            user_id: User ID to analyze
            time_range: Time range for analytics (24h, 7d, 30d, all)
            
        Returns:
            Dict containing user analytics
        """
        threshold = self._get_time_threshold(time_range)
        
        # Get user's reported incidents
        reported = self.db.query(Incident).filter(
            Incident.reporter_id == user_id,
            Incident.created_at >= threshold
        ).all()
        
        # Get user's assigned incidents
        assigned = self.db.query(Incident).filter(
            Incident.assigned_to == user_id,
            Incident.created_at >= threshold
        ).all()
        
        # Get user's incident responses
        responses = self.db.query(IncidentResponse).filter(
            IncidentResponse.responder_id == user_id,
            IncidentResponse.assigned_at >= threshold
        ).all()
        
        # Calculate response metrics
        avg_response_time = 0
        avg_resolution_time = 0
        if responses:
            response_times = [r.time_to_respond for r in responses if r.time_to_respond]
            resolution_times = [r.time_to_resolve for r in responses if r.time_to_resolve]
            
            if response_times:
                avg_response_time = sum(response_times) / len(response_times)
            if resolution_times:
                avg_resolution_time = sum(resolution_times) / len(resolution_times)
        
        return {
            "reported_incidents": {
                "total": len(reported),
                "by_severity": self._count_by_field(reported, "severity"),
                "by_status": self._count_by_field(reported, "status")
            },
            "assigned_incidents": {
                "total": len(assigned),
                "by_severity": self._count_by_field(assigned, "severity"),
                "by_status": self._count_by_field(assigned, "status"),
                "resolution_rate": self._calculate_resolution_rate(assigned)
            },
            "response_metrics": {
                "total_responses": len(responses),
                "avg_response_time": avg_response_time,
                "avg_resolution_time": avg_resolution_time,
                "by_priority": self._count_by_field(responses, "response_priority")
            },
            "time_range": time_range
        }

    def get_team_analytics(self, time_range: str = "30d") -> Dict[str, Any]:
        """Get analytics for the entire team.
        
        Args:
            time_range: Time range for analytics (24h, 7d, 30d, all)
            
        Returns:
            Dict containing team analytics
        """
        threshold = self._get_time_threshold(time_range)
        
        # Get all users with their responses
        users = self.db.query(User).all()
        user_metrics = {}
        
        for user in users:
            # Get user's incident responses
            responses = self.db.query(IncidentResponse).filter(
                IncidentResponse.responder_id == user.id,
                IncidentResponse.assigned_at >= threshold
            ).all()
            
            # Calculate user's metrics
            response_times = [r.time_to_respond for r in responses if r.time_to_respond]
            resolution_times = [r.time_to_resolve for r in responses if r.time_to_resolve]
            
            user_metrics[user.id] = {
                "name": user.name,
                "email": user.email,
                "department": user.profile.department if user.profile else None,
                "role": user.profile.role if user.profile else None,
                "metrics": {
                    "total_responses": len(responses),
                    "avg_response_time": sum(response_times) / len(response_times) if response_times else 0,
                    "avg_resolution_time": sum(resolution_times) / len(resolution_times) if resolution_times else 0,
                    "response_distribution": self._count_by_field(responses, "response_priority")
                }
            }
        
        # Calculate team-wide metrics
        all_responses = self.db.query(IncidentResponse).filter(
            IncidentResponse.assigned_at >= threshold
        ).all()
        
        return {
            "team_members": len(users),
            "total_responses": len(all_responses),
            "member_metrics": user_metrics,
            "workload_distribution": self._calculate_workload_distribution(user_metrics),
            "time_range": time_range
        }

    def get_user_engagement_metrics(self, time_range: str = "30d") -> Dict[str, Any]:
        """Get user engagement metrics across the platform.
        
        Args:
            time_range: Time range for analytics (24h, 7d, 30d, all)
            
        Returns:
            Dict containing engagement metrics
        """
        threshold = self._get_time_threshold(time_range)
        
        # Get all users
        users = self.db.query(User).all()
        engagement_metrics = {}
        
        for user in users:
            # Get user's activities
            reported = self.db.query(Incident).filter(
                Incident.reporter_id == user.id,
                Incident.created_at >= threshold
            ).count()
            
            assigned = self.db.query(Incident).filter(
                Incident.assigned_to == user.id,
                Incident.created_at >= threshold
            ).count()
            
            responses = self.db.query(IncidentResponse).filter(
                IncidentResponse.responder_id == user.id,
                IncidentResponse.assigned_at >= threshold
            ).count()
            
            actions = self.db.query(ResponseAction).filter(
                ResponseAction.performed_by == user.id,
                ResponseAction.performed_at >= threshold
            ).count()
            
            engagement_metrics[user.id] = {
                "name": user.name,
                "email": user.email,
                "metrics": {
                    "reported_incidents": reported,
                    "assigned_incidents": assigned,
                    "incident_responses": responses,
                    "response_actions": actions,
                    "total_engagement": reported + assigned + responses + actions
                }
            }
        
        return {
            "user_engagement": engagement_metrics,
            "time_range": time_range
        }

    def _count_by_field(self, items: List[Any], field: str) -> Dict[str, int]:
        """Helper method to count items by a field value."""
        counts = {}
        for item in items:
            value = getattr(item, field)
            counts[value] = counts.get(value, 0) + 1
        return counts

    def _calculate_resolution_rate(self, incidents: List[Incident]) -> float:
        """Calculate the resolution rate for a list of incidents."""
        if not incidents:
            return 0.0
        resolved = sum(1 for i in incidents if i.status in ['resolved', 'closed'])
        return (resolved / len(incidents)) * 100

    def _calculate_workload_distribution(self, user_metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate workload distribution across team members."""
        total_responses = sum(
            m['metrics']['total_responses'] 
            for m in user_metrics.values()
        )
        
        if total_responses == 0:
            return {"distribution": {}, "balance_score": 0}
        
        distribution = {
            user_id: {
                "name": metrics["name"],
                "percentage": (metrics['metrics']['total_responses'] / total_responses) * 100
            }
            for user_id, metrics in user_metrics.items()
        }
        
        # Calculate workload balance score (0-100)
        # Perfect balance would be equal distribution among team members
        ideal_percentage = 100 / len(user_metrics) if user_metrics else 0
        deviations = [
            abs(d["percentage"] - ideal_percentage) 
            for d in distribution.values()
        ]
        balance_score = 100 - (sum(deviations) / len(deviations)) if deviations else 0
        
        return {
            "distribution": distribution,
            "balance_score": balance_score
        }

    def get_recent_incidents(self, limit: int = 10, offset: int = 0) -> Dict[str, Any]:
        """Get recent incidents with user information."""
        print("[DEBUG] Starting get_recent_incidents")
        
        # Get total count
        total_count = self.db.query(Incident).count()
        print(f"[DEBUG] Total incidents in database: {total_count}")
        
        # Get paginated incidents
        incidents = self.db.query(Incident)\
            .order_by(Incident.created_at.desc())\
            .offset(offset)\
            .limit(limit)\
            .all()
            
        print(f"[DEBUG] Successfully queried {len(incidents)} incidents")
        
        # Format response
        formatted_incidents = []
        for incident in incidents:
            try:
                # Get reporter info
                reporter = None
                if incident.reporter_id:
                    try:
                        reporter = self.user_service.get_user(incident.reporter_id)
                        print(f"[DEBUG] Got reporter info for incident {incident.id}: {reporter.id if reporter else 'None'}")
                    except Exception as e:
                        print(f"[WARNING] Failed to get reporter info for incident {incident.id}: {str(e)}")
                
                # Format incident data
                incident_data = {
                    "id": incident.id,
                    "title": incident.title,
                    "status": incident.status,
                    "severity": incident.severity,
                    "timestamp": incident.created_at.isoformat(),
                    "is_system_report": incident.reporter_id == "system"
                }
                
                # Add user info if available
                if reporter and reporter.id != "system":
                    incident_data["user"] = {
                        "name": reporter.name,
                        "email": reporter.email,
                        "avatar": reporter.profile.avatar_url if reporter.profile else None
                    }
                else:
                    incident_data["user"] = {
                        "name": "System",
                        "email": "system@vessa.io",
                        "avatar": None
                    }
                    
                formatted_incidents.append(incident_data)
                print(f"[DEBUG] Successfully formatted incident {incident.id}")
                
            except Exception as e:
                print(f"[ERROR] Failed to format incident {incident.id}: {str(e)}")
                continue
        
        response = {
            "incidents": formatted_incidents,
            "total_count": total_count,
            "has_more": (offset + limit) < total_count
        }
        
        print(f"[DEBUG] Successfully built response with {len(formatted_incidents)} incidents")
        return response

    def _get_time_threshold(self, time_range: str) -> datetime:
        """Get datetime threshold from time range string.
        
        Args:
            time_range: Time range string (24h, 7d, 30d, all)
            
        Returns:
            Datetime threshold
        """
        now = datetime.utcnow()
        if time_range == "24h":
            return now - timedelta(hours=24)
        elif time_range == "7d":
            return now - timedelta(days=7)
        elif time_range == "30d":
            return now - timedelta(days=30)
        return datetime.min  # For "all" or invalid ranges

    def make_json_serializable(self, obj):
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, dict):
            return {k: self.make_json_serializable(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self.make_json_serializable(v) for v in obj]
        else:
            return obj 