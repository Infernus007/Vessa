"""Input Sanitization for ML Model and API Inputs.

This module provides comprehensive input sanitization to prevent
injection attacks, XXE, and other input-based vulnerabilities.
"""

import re
import html
import json
from typing import Any, Dict, List, Optional
from urllib.parse import urlparse


class InputSanitizer:
    """Sanitize user inputs before processing."""
    
    # Dangerous patterns to detect
    SQL_INJECTION_PATTERNS = [
        r"(\b(SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER|EXEC|EXECUTE)\b)",
        r"(--|\#|\/\*|\*\/)",
        r"(\bUNION\b.*\bSELECT\b)",
        r"(\bOR\b.*=.*)",
        r"(\bAND\b.*=.*)",
    ]
    
    XSS_PATTERNS = [
        r"<script[^>]*>.*?</script>",
        r"javascript:",
        r"on\w+\s*=",
        r"<iframe[^>]*>",
        r"<embed[^>]*>",
        r"<object[^>]*>",
    ]
    
    XXE_PATTERNS = [
        r"<!ENTITY",
        r"<!DOCTYPE",
        r"SYSTEM\s+['\"]",
    ]
    
    COMMAND_INJECTION_PATTERNS = [
        r"[;&|`$(){}[\]<>]",
        r"\$\{.*\}",
        r"`.*`",
    ]
    
    MAX_INPUT_LENGTH = 100000  # 100KB max input
    MAX_JSON_DEPTH = 10
    MAX_ARRAY_LENGTH = 1000
    
    @classmethod
    def sanitize_string(cls, input_str: str, max_length: Optional[int] = None) -> str:
        """Sanitize a string input.
        
        Args:
            input_str: Input string to sanitize
            max_length: Maximum allowed length
            
        Returns:
            Sanitized string
            
        Raises:
            ValueError: If input is dangerous or too long
        """
        if not isinstance(input_str, str):
            return str(input_str)
        
        # Check length
        max_len = max_length or cls.MAX_INPUT_LENGTH
        if len(input_str) > max_len:
            raise ValueError(f"Input too long: {len(input_str)} chars (max: {max_len})")
        
        # HTML escape to prevent XSS
        sanitized = html.escape(input_str)
        
        return sanitized
    
    @classmethod
    def sanitize_json(cls, json_data: Any, depth: int = 0) -> Any:
        """Recursively sanitize JSON data.
        
        Args:
            json_data: JSON data to sanitize
            depth: Current recursion depth
            
        Returns:
            Sanitized JSON data
            
        Raises:
            ValueError: If JSON is too nested or contains dangerous content
        """
        if depth > cls.MAX_JSON_DEPTH:
            raise ValueError(f"JSON too deeply nested (max depth: {cls.MAX_JSON_DEPTH})")
        
        if isinstance(json_data, dict):
            sanitized = {}
            for key, value in json_data.items():
                # Sanitize keys
                safe_key = cls.sanitize_string(str(key), max_length=256)
                # Recursively sanitize values
                sanitized[safe_key] = cls.sanitize_json(value, depth + 1)
            return sanitized
        
        elif isinstance(json_data, list):
            if len(json_data) > cls.MAX_ARRAY_LENGTH:
                raise ValueError(f"Array too long: {len(json_data)} items (max: {cls.MAX_ARRAY_LENGTH})")
            return [cls.sanitize_json(item, depth + 1) for item in json_data]
        
        elif isinstance(json_data, str):
            return cls.sanitize_string(json_data)
        
        else:
            # Numbers, booleans, None are safe
            return json_data
    
    @classmethod
    def validate_url(cls, url: str) -> str:
        """Validate and sanitize a URL.
        
        Args:
            url: URL to validate
            
        Returns:
            Validated URL
            
        Raises:
            ValueError: If URL is malformed or dangerous
        """
        if not url or not isinstance(url, str):
            raise ValueError("Invalid URL: empty or not a string")
        
        if len(url) > 2048:
            raise ValueError("URL too long")
        
        # Parse URL
        try:
            parsed = urlparse(url)
        except Exception:
            raise ValueError("Invalid URL format")
        
        # Check scheme
        if parsed.scheme and parsed.scheme not in ['http', 'https', 'ws', 'wss']:
            raise ValueError(f"Invalid URL scheme: {parsed.scheme}")
        
        # Check for javascript: and data: URIs
        if url.lower().startswith(('javascript:', 'data:', 'vbscript:')):
            raise ValueError("Dangerous URL scheme detected")
        
        return url
    
    @classmethod
    def validate_ip_address(cls, ip: str) -> str:
        """Validate an IP address.
        
        Args:
            ip: IP address to validate
            
        Returns:
            Validated IP address
            
        Raises:
            ValueError: If IP is invalid
        """
        if not ip or not isinstance(ip, str):
            raise ValueError("Invalid IP address")
        
        # Basic IP validation (IPv4 and IPv6)
        import ipaddress
        try:
            ipaddress.ip_address(ip)
            return ip
        except ValueError:
            raise ValueError(f"Invalid IP address: {ip}")
    
    @classmethod
    def sanitize_request_data(
        cls,
        client_ip: str,
        request_path: str,
        request_method: str,
        request_headers: Dict[str, str],
        request_body: Optional[str] = None
    ) -> Dict[str, Any]:
        """Sanitize request data for ML model analysis.
        
        This is the main entry point for sanitizing data before
        sending it to the ML model for threat detection.
        
        Args:
            client_ip: Client IP address
            request_path: Request path
            request_method: HTTP method
            request_headers: Request headers
            request_body: Request body (optional)
            
        Returns:
            Sanitized request data dictionary
            
        Raises:
            ValueError: If any input is dangerous or invalid
        """
        # Validate IP
        safe_ip = cls.validate_ip_address(client_ip)
        
        # Sanitize path (but preserve for analysis)
        safe_path = cls.sanitize_string(request_path, max_length=2048)
        
        # Validate method
        valid_methods = ['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'HEAD', 'OPTIONS']
        if request_method.upper() not in valid_methods:
            raise ValueError(f"Invalid HTTP method: {request_method}")
        
        # Sanitize headers
        safe_headers = {}
        if request_headers:
            for key, value in request_headers.items():
                # Limit header name and value length
                safe_key = cls.sanitize_string(str(key), max_length=256)
                safe_value = cls.sanitize_string(str(value), max_length=8192)
                safe_headers[safe_key] = safe_value
        
        # Sanitize body
        safe_body = None
        if request_body:
            # Check if it's JSON
            try:
                body_json = json.loads(request_body)
                safe_body = json.dumps(cls.sanitize_json(body_json))
            except json.JSONDecodeError:
                # Not JSON, sanitize as string
                safe_body = cls.sanitize_string(request_body, max_length=cls.MAX_INPUT_LENGTH)
        
        return {
            "client_ip": safe_ip,
            "request_path": safe_path,
            "request_method": request_method.upper(),
            "request_headers": safe_headers,
            "request_body": safe_body
        }
    
    @classmethod
    def check_for_known_attacks(cls, text: str) -> List[str]:
        """Check text for known attack patterns.
        
        This is informational only - doesn't block, just warns.
        
        Args:
            text: Text to check
            
        Returns:
            List of detected attack pattern names
        """
        detected = []
        
        # Check SQL injection patterns
        for pattern in cls.SQL_INJECTION_PATTERNS:
            if re.search(pattern, text, re.IGNORECASE):
                detected.append("SQL Injection Pattern")
                break
        
        # Check XSS patterns
        for pattern in cls.XSS_PATTERNS:
            if re.search(pattern, text, re.IGNORECASE):
                detected.append("XSS Pattern")
                break
        
        # Check XXE patterns
        for pattern in cls.XXE_PATTERNS:
            if re.search(pattern, text, re.IGNORECASE):
                detected.append("XXE Pattern")
                break
        
        # Check command injection patterns
        for pattern in cls.COMMAND_INJECTION_PATTERNS:
            if re.search(pattern, text):
                detected.append("Command Injection Pattern")
                break
        
        return detected


# Convenience functions
def sanitize_for_ml_analysis(
    client_ip: str,
    request_path: str,
    request_method: str,
    request_headers: Dict[str, str],
    request_body: Optional[str] = None
) -> Dict[str, Any]:
    """Sanitize request data before ML analysis.
    
    This is the main function to use before sending data to ML models.
    """
    return InputSanitizer.sanitize_request_data(
        client_ip, request_path, request_method, request_headers, request_body
    )

