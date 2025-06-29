"""
Client Integration Example

This example shows how client systems can integrate with the enhanced VESSA threat intelligence analysis.
"""

import requests
import json
from typing import Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime

@dataclass
class RequestData:
    """Data structure for request analysis."""
    source_ip: str
    request_path: str
    request_method: str
    headers: Optional[Dict[str, str]] = None
    body: Optional[Dict[str, Any]] = None
    user_agent: Optional[str] = None

class VESSAThreatAnalyzer:
    """Client-side threat analyzer that integrates with VESSA platform."""
    
    def __init__(self, api_base_url: str, api_key: str):
        """Initialize the threat analyzer.
        
        Args:
            api_base_url: Base URL of VESSA API (e.g., "http://localhost:8000")
            api_key: API key for authentication
        """
        self.api_base_url = api_base_url.rstrip('/')
        self.api_key = api_key
        self.session = requests.Session()
        self.session.headers.update({
            'X-API-Key': api_key,
            'Content-Type': 'application/json'
        })
    
    def analyze_request(self, request_data: RequestData) -> Dict[str, Any]:
        """Analyze a request for threats.
        
        Args:
            request_data: Request data to analyze
            
        Returns:
            Analysis results
        """
        payload = {
            "source_ip": request_data.source_ip,
            "request_path": request_data.request_path,
            "request_method": request_data.request_method,
            "headers": request_data.headers or {},
            "body": request_data.body or {},
            "user_agent": request_data.user_agent or ""
        }
        
        try:
            response = self.session.post(
                f"{self.api_base_url}/incidents/analyze-request",
                json=payload
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {
                "error": f"Analysis failed: {str(e)}",
                "threat_score": 0,
                "should_block": False
            }
    
    def check_ip_reputation(self, ip: str) -> Dict[str, Any]:
        """Check IP reputation.
        
        Args:
            ip: IP address to check
            
        Returns:
            Reputation analysis results
        """
        payload = {"ip": ip}
        
        try:
            response = self.session.post(
                f"{self.api_base_url}/threat-intelligence/ip-reputation",
                json=payload
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {
                "error": f"IP reputation check failed: {str(e)}",
                "is_malicious": False,
                "threat_score": 0
            }
    
    def check_domain_reputation(self, domain: str) -> Dict[str, Any]:
        """Check domain reputation.
        
        Args:
            domain: Domain to check
            
        Returns:
            Reputation analysis results
        """
        payload = {"domain": domain}
        
        try:
            response = self.session.post(
                f"{self.api_base_url}/threat-intelligence/domain-reputation",
                json=payload
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {
                "error": f"Domain reputation check failed: {str(e)}",
                "is_malicious": False,
                "threat_score": 0
            }
    
    def match_yara_rules(self, content: str) -> Dict[str, Any]:
        """Match content against YARA rules.
        
        Args:
            content: Content to analyze
            
        Returns:
            YARA matching results
        """
        payload = {"content": content}
        
        try:
            response = self.session.post(
                f"{self.api_base_url}/threat-intelligence/yara-match",
                json=payload
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {
                "error": f"YARA matching failed: {str(e)}",
                "is_suspicious": False,
                "total_matches": 0
            }

# Example middleware integration
class VESSAMiddleware:
    """Example middleware that integrates VESSA threat analysis."""
    
    def __init__(self, vessa_analyzer: VESSAThreatAnalyzer):
        """Initialize the middleware.
        
        Args:
            vessa_analyzer: VESSA threat analyzer instance
        """
        self.analyzer = vessa_analyzer
    
    def process_request(self, request_data: RequestData) -> Dict[str, Any]:
        """Process a request through threat analysis.
        
        Args:
            request_data: Request data to process
            
        Returns:
            Processing results with decision
        """
        # Perform threat analysis
        analysis = self.analyzer.analyze_request(request_data)
        
        # Make decision based on analysis
        decision = self._make_decision(analysis)
        
        return {
            "request_id": f"req_{datetime.now().timestamp()}",
            "analysis": analysis,
            "decision": decision,
            "timestamp": datetime.now().isoformat()
        }
    
    def _make_decision(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Make a decision based on threat analysis.
        
        Args:
            analysis: Threat analysis results
            
        Returns:
            Decision details
        """
        threat_score = analysis.get("threat_score", 0)
        
        if threat_score >= 75:
            return {
                "action": "block",
                "reason": "High threat score detected",
                "confidence": analysis.get("confidence", 0.0)
            }
        elif threat_score >= 50:
            return {
                "action": "challenge",
                "reason": "Medium threat score detected",
                "confidence": analysis.get("confidence", 0.0)
            }
        elif threat_score >= 25:
            return {
                "action": "log",
                "reason": "Low threat score detected",
                "confidence": analysis.get("confidence", 0.0)
            }
        else:
            return {
                "action": "allow",
                "reason": "No threats detected",
                "confidence": 1.0
            }

# Example usage
def example_usage():
    """Example of how to use the VESSA threat analyzer."""
    
    # Initialize the analyzer
    analyzer = VESSAThreatAnalyzer(
        api_base_url="http://localhost:8000",
        api_key="your-api-key-here"
    )
    
    # Example 1: Analyze a suspicious request
    suspicious_request = RequestData(
        source_ip="192.168.1.100",  # Known malicious IP
        request_path="/admin?cmd=whoami",
        request_method="GET",
        headers={
            "Host": "example.com",
            "User-Agent": "curl/7.68.0"
        },
        user_agent="curl/7.68.0"
    )
    
    print("=== Analyzing Suspicious Request ===")
    result = analyzer.analyze_request(suspicious_request)
    print(f"Threat Score: {result.get('threat_score', 0)}")
    print(f"Should Block: {result.get('should_block', False)}")
    print(f"Findings: {result.get('findings', [])}")
    print(f"Analysis Methods: {result.get('analysis_methods', [])}")
    
    # Example 2: Check IP reputation
    print("\n=== Checking IP Reputation ===")
    ip_result = analyzer.check_ip_reputation("192.168.1.100")
    print(f"IP: {ip_result.get('ip', 'unknown')}")
    print(f"Is Malicious: {ip_result.get('is_malicious', False)}")
    print(f"Threat Score: {ip_result.get('threat_score', 0)}")
    print(f"Categories: {ip_result.get('categories', [])}")
    
    # Example 3: Check domain reputation
    print("\n=== Checking Domain Reputation ===")
    domain_result = analyzer.check_domain_reputation("malware.example.com")
    print(f"Domain: {domain_result.get('domain', 'unknown')}")
    print(f"Is Malicious: {domain_result.get('is_malicious', False)}")
    print(f"Threat Score: {domain_result.get('threat_score', 0)}")
    print(f"Categories: {domain_result.get('categories', [])}")
    
    # Example 4: YARA rule matching
    print("\n=== YARA Rule Matching ===")
    yara_result = analyzer.match_yara_rules("GET /admin?cmd=whoami HTTP/1.1")
    print(f"Is Suspicious: {yara_result.get('is_suspicious', False)}")
    print(f"Total Matches: {yara_result.get('total_matches', 0)}")
    print(f"Matches: {yara_result.get('matches', [])}")
    
    # Example 5: Middleware integration
    print("\n=== Middleware Integration ===")
    middleware = VESSAMiddleware(analyzer)
    decision = middleware.process_request(suspicious_request)
    print(f"Decision: {decision['decision']['action']}")
    print(f"Reason: {decision['decision']['reason']}")
    print(f"Confidence: {decision['decision']['confidence']}")

if __name__ == "__main__":
    example_usage() 