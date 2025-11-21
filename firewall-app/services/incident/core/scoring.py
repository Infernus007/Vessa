"""Threat scoring constants and logic.

This module defines standard threat scores and types for the WAF.
"""

from enum import Enum

class ThreatType(str, Enum):
    SQL_INJECTION = "sql_injection"
    XSS = "xss"
    COMMAND_INJECTION = "command_injection"
    PATH_TRAVERSAL = "path_traversal"
    NOSQL_INJECTION = "nosql_injection"
    SUSPICIOUS = "suspicious"
    SAFE = "safe"

class ThreatScore:
    """Standard threat scores (0.0 - 1.0)."""
    
    # High severity threats
    COMMAND_INJECTION = 0.90
    SQL_INJECTION = 0.85
    PATH_TRAVERSAL = 0.85
    XSS = 0.80
    NOSQL_INJECTION = 0.80
    
    # Medium/Low severity indicators
    SUSPICIOUS_USER_AGENT = 0.20
    ADMIN_ACCESS_ATTEMPT = 0.20
    SUSPICIOUS_PROXY = 0.10
    
    # Thresholds
    BLOCKING_THRESHOLD = 0.50
    SUSPICIOUS_THRESHOLD = 0.30

def normalize_score(score: float) -> float:
    """Normalize score to 0.0 - 1.0 range."""
    return min(max(score, 0.0), 1.0)
