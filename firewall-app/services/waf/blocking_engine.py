"""Blocking Engine - Handles request blocking and response generation.

This module provides customizable blocking responses and actions.
"""

from typing import Dict, Any, Optional
from enum import Enum
import time


class BlockPage(str, Enum):
    """Built-in block page templates."""
    SIMPLE = "simple"
    DETAILED = "detailed"
    CUSTOM = "custom"


class BlockingEngine:
    """Engine for handling blocked requests and generating responses."""
    
    def __init__(self, block_page: BlockPage = BlockPage.SIMPLE):
        """Initialize blocking engine.
        
        Args:
            block_page: Block page template to use
        """
        self.block_page = block_page
        self.custom_block_html: Optional[str] = None
    
    def generate_block_response(
        self,
        threat_type: str,
        threat_score: float,
        findings: list,
        request_id: str,
        client_ip: str
    ) -> Dict[str, Any]:
        """Generate block response.
        
        Args:
            threat_type: Type of threat detected
            threat_score: Threat score
            findings: List of findings
            request_id: Unique request ID
            client_ip: Client IP address
            
        Returns:
            Response dictionary
        """
        if self.block_page == BlockPage.SIMPLE:
            return self._simple_block_response(request_id)
        elif self.block_page == BlockPage.DETAILED:
            return self._detailed_block_response(
                threat_type, threat_score, findings, request_id, client_ip
            )
        else:
            return self._custom_block_response(request_id)
    
    def _simple_block_response(self, request_id: str) -> Dict[str, Any]:
        """Generate simple block response."""
        return {
            "error": "Forbidden",
            "message": "Your request has been blocked by our security system.",
            "request_id": request_id,
            "timestamp": int(time.time())
        }
    
    def _detailed_block_response(
        self,
        threat_type: str,
        threat_score: float,
        findings: list,
        request_id: str,
        client_ip: str
    ) -> Dict[str, Any]:
        """Generate detailed block response with threat information."""
        return {
            "error": "Forbidden",
            "message": "Your request has been blocked by our Web Application Firewall.",
            "details": {
                "threat_type": threat_type,
                "threat_score": round(threat_score, 3),
                "reason": self._get_friendly_reason(threat_type),
                "blocked_at": int(time.time())
            },
            "request_id": request_id,
            "support": "If you believe this is an error, please contact support with the request ID."
        }
    
    def _custom_block_response(self, request_id: str) -> Dict[str, Any]:
        """Generate custom block response."""
        return {
            "error": "Forbidden",
            "message": self.custom_block_html or "Request blocked",
            "request_id": request_id
        }
    
    def _get_friendly_reason(self, threat_type: str) -> str:
        """Get user-friendly explanation for threat type.
        
        Args:
            threat_type: Threat type
            
        Returns:
            User-friendly explanation
        """
        reasons = {
            "sql_injection": "Potential SQL injection attack detected",
            "xss": "Potential cross-site scripting (XSS) attack detected",
            "path_traversal": "Potential path traversal attack detected",
            "command_injection": "Potential command injection attack detected",
            "nosql_injection": "Potential NoSQL injection attack detected",
            "suspicious": "Suspicious request pattern detected",
            "blacklisted_ip": "Your IP address is on our security blocklist",
            "rate_limit": "Too many requests from your IP address"
        }
        
        return reasons.get(threat_type, "Security policy violation detected")
    
    def set_custom_block_html(self, html: str) -> None:
        """Set custom HTML for block pages.
        
        Args:
            html: Custom HTML content
        """
        self.custom_block_html = html
        self.block_page = BlockPage.CUSTOM

