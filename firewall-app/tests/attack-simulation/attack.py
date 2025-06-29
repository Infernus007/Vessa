#!/usr/bin/env python3

import requests
import time
import argparse
import json
from typing import Dict, List
import random
from datetime import datetime

# Enhanced attack payloads with more sophisticated patterns
SQL_INJECTION_PAYLOADS = [
    "' OR '1'='1",
    "admin' --",
    "' UNION SELECT * FROM users --",
    "'; DROP TABLE users --",
    "' OR 'x'='x",
    "1' UNION SELECT username,password FROM users--",
    "admin' OR 1=1#",
    "' OR 1=1 LIMIT 1--",
    "'; EXEC xp_cmdshell('dir');--",
    "1' AND (SELECT COUNT(*) FROM users)>0--"
]

XSS_PAYLOADS = [
    "<script>alert('xss')</script>",
    "<img src=x onerror=alert('xss')>",
    "javascript:alert('xss')",
    "<svg/onload=alert('xss')>",
    "'\\'><script>alert('xss')</script>",
    "<iframe src=javascript:alert('xss')>",
    "<body onload=alert('xss')>",
    "<input onfocus=alert('xss') autofocus>",
    "<details open ontoggle=alert('xss')>",
    "<video><source onerror=alert('xss')>"
]

PATH_TRAVERSAL_PAYLOADS = [
    "../../../etc/passwd",
    "..\\..\\..\\windows\\system32\\config\\sam",
    "....//....//....//etc/hosts",
    "%2e%2e%2f%2e%2e%2f%2e%2e%2fetc%2fpasswd",
    "..%252f..%252f..%252fetc%252fpasswd",
    "..%c0%af..%c0%af..%c0%afetc%c0%afpasswd",
    "..%255c..%255c..%255cwindows%255csystem32%255cconfig%255csam",
    "..%5c..%5c..%5cwindows%5csystem32%5cconfig%5csam",
    "..%2f..%2f..%2f..%2f..%2f..%2f..%2f..%2f..%2fetc%2fpasswd",
    "..%c1%9c..%c1%9c..%c1%9cwindows%c1%9csystem32%c1%9cconfig%c1%9csam"
]

COMMAND_INJECTION_PAYLOADS = [
    "; cat /etc/passwd",
    "| cat /etc/passwd",
    "`cat /etc/passwd`",
    "$(cat /etc/passwd)",
    "&& cat /etc/passwd",
    "|| cat /etc/passwd",
    "; whoami",
    "| whoami",
    "`whoami`",
    "$(whoami)",
    "; ping -c 1 192.168.1.1",
    "| ping -c 1 192.168.1.1",
    "`ping -c 1 192.168.1.1`",
    "$(ping -c 1 192.168.1.1)"
]

NOSQL_INJECTION_PAYLOADS = [
    '{"$ne": null}',
    '{"$gt": ""}',
    '{"$where": "1==1"}',
    '{"$regex": ".*"}',
    '{"$exists": true}',
    '{"$in": ["admin", "user"]}',
    '{"$or": [{"username": "admin"}, {"username": "user"}]}',
    '{"$and": [{"username": {"$ne": null}}, {"password": {"$ne": null}}]}',
    '{"$where": "this.username == this.password"}',
    '{"$where": "sleep(1000)"}'
]

# Malicious IPs and domains for reputation testing
MALICIOUS_IPS = [
    "185.220.101.1",  # Known malicious IP
    "45.95.147.1",    # Known malicious IP
    "185.220.102.1",  # Known malicious IP
    "45.95.147.2",    # Known malicious IP
    "185.220.103.1"   # Known malicious IP
]

MALICIOUS_DOMAINS = [
    "malware.example.com",
    "phishing.test.com",
    "botnet.suspicious.net",
    "malicious.test.org",
    "evil.example.net"
]

# Suspicious User Agents
SUSPICIOUS_USER_AGENTS = [
    "curl/7.68.0",
    "python-requests/2.25.1",
    "wget/1.20.3",
    "Mozilla/5.0 (compatible; Nmap Scripting Engine; https://nmap.org/book/nse.html)",
    "Mozilla/5.0 (compatible; masscan/1.0; https://github.com/robertdavidgraham/masscan)",
    "sqlmap/1.4.12#stable (http://sqlmap.org)",
    "Nikto/2.1.6",
    "OWASP ZAP",
    "Burp Suite Professional",
    "Acunetix WVS"
]

class AttackSimulator:
    """Simulates various types of attacks with enhanced threat intelligence testing."""

    def __init__(self, target_url: str, api_key: str):
        """Initialize attack simulator.
        
        Args:
            target_url: Target URL
            api_key: API key for authentication
        """
        self.target_url = target_url.rstrip('/')
        self.headers = {
            'X-API-Key': api_key,
            'Content-Type': 'application/json'
        }

    def send_attack(self, payload: Dict, attack_type: str) -> requests.Response:
        """Send an attack request to the analyze-request endpoint.
        
        Args:
            payload: Request payload for analysis
            attack_type: Type of attack being simulated
            
        Returns:
            Response from server
        """
        url = f"{self.target_url}/incidents/analyze-request"
            
        try:
            response = requests.post(
                url=url,
                json=payload,
                headers=self.headers,
                timeout=10
            )
            print(f"\n[ATTACK] {attack_type.upper()} - {payload.get('request_path', 'unknown')}")
            print(f"Status: {response.status_code}")
            
            # Print analysis results
            if response.status_code == 200:
                analysis = response.json()
                print(f"Threat Score: {analysis.get('threat_score', 0):.2f}")
                print(f"Threat Type: {analysis.get('threat_type', 'unknown')}")
                print(f"Should Block: {analysis.get('should_block', False)}")
                print(f"Analysis Methods: {analysis.get('analysis_methods', [])}")
                print(f"Findings: {len(analysis.get('findings', []))} findings")
                for finding in analysis.get('findings', [])[:3]:  # Show first 3 findings
                    print(f"  - {finding}")
                if analysis.get('incident_id'):
                    print(f"Incident Created: {analysis['incident_id']}")
                if analysis.get('confidence'):
                    print(f"Confidence: {analysis['confidence']:.2f}")
            else:
                print(f"Error Response: {response.text}")
                
            return response
        except Exception as e:
            print(f"Error sending attack: {str(e)}")
            return None

    def create_base_payload(self, attack_type: str) -> Dict:
        """Create base payload structure for attack request.
        
        Args:
            attack_type: Type of attack being simulated
            
        Returns:
            Base payload dictionary
        """
        return {
            "request_method": "POST",
            "request_url": f"{self.target_url}/api/users",
            "request_path": "/api/users",
            "request_headers": {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                "Content-Type": "application/json",
                "X-Forwarded-For": "192.168.1.100",
                "X-API-Key": self.headers["X-API-Key"]
            },
            "request_query_params": {},
            "request_body": {},
            "client_ip": "192.168.1.100",
            "timestamp": datetime.utcnow().isoformat(),
            "service_name": "attack-simulation",
            "service_version": "1.0.0",
            "attack_type": attack_type
        }

    def sql_injection_attack(self):
        """Simulate SQL injection attacks."""
        print("\n=== SQL INJECTION ATTACKS ===")
        for i, payload in enumerate(SQL_INJECTION_PAYLOADS, 1):
            base_payload = self.create_base_payload("sql_injection")
            base_payload["request_body"] = {
                "username": payload,
                "password": "' OR '1'='1"
            }
            base_payload["request_query_params"] = {
                "id": "1 OR 1=1",
                "search": payload
            }
            base_payload["request_path"] = f"/api/users?search={payload}"
            
            self.send_attack(base_payload, f"sql_injection_{i}")
            time.sleep(0.5)

    def xss_attack(self):
        """Simulate XSS attacks."""
        print("\n=== XSS ATTACKS ===")
        for i, payload in enumerate(XSS_PAYLOADS, 1):
            base_payload = self.create_base_payload("xss")
            base_payload["request_body"] = {
                "comment": payload,
                "user_input": payload,
                "message": payload
            }
            base_payload["request_headers"]["Referer"] = f"javascript:{payload}"
            base_payload["request_headers"]["User-Agent"] = random.choice(SUSPICIOUS_USER_AGENTS)
            
            self.send_attack(base_payload, f"xss_{i}")
            time.sleep(0.5)

    def path_traversal_attack(self):
        """Simulate path traversal attacks."""
        print("\n=== PATH TRAVERSAL ATTACKS ===")
        for i, payload in enumerate(PATH_TRAVERSAL_PAYLOADS, 1):
            base_payload = self.create_base_payload("path_traversal")
            base_payload["request_path"] = f"/api/files/{payload}"
            base_payload["request_query_params"] = {
                "file": payload,
                "path": payload,
                "download": payload
            }
            base_payload["request_body"] = {
                "filepath": payload,
                "directory": payload
            }
            
            self.send_attack(base_payload, f"path_traversal_{i}")
            time.sleep(0.5)

    def command_injection_attack(self):
        """Simulate command injection attacks."""
        print("\n=== COMMAND INJECTION ATTACKS ===")
        for i, payload in enumerate(COMMAND_INJECTION_PAYLOADS, 1):
            base_payload = self.create_base_payload("command_injection")
            base_payload["request_body"] = {
                "command": payload,
                "input": payload,
                "system": payload
            }
            base_payload["request_query_params"] = {
                "cmd": payload,
                "exec": payload
            }
            base_payload["request_path"] = f"/api/system/execute?cmd={payload}"
            
            self.send_attack(base_payload, f"command_injection_{i}")
            time.sleep(0.5)

    def nosql_injection_attack(self):
        """Simulate NoSQL injection attacks."""
        print("\n=== NOSQL INJECTION ATTACKS ===")
        for i, payload in enumerate(NOSQL_INJECTION_PAYLOADS, 1):
            base_payload = self.create_base_payload("nosql_injection")
            base_payload["request_body"] = {
                "query": payload,
                "filter": payload,
                "criteria": payload
            }
            base_payload["request_headers"]["Content-Type"] = "application/json"
            
            self.send_attack(base_payload, f"nosql_injection_{i}")
            time.sleep(0.5)

    def malicious_ip_attack(self):
        """Simulate attacks from known malicious IPs."""
        print("\n=== MALICIOUS IP ATTACKS ===")
        for i, ip in enumerate(MALICIOUS_IPS, 1):
            base_payload = self.create_base_payload("malicious_ip")
            base_payload["client_ip"] = ip
            base_payload["request_headers"]["X-Forwarded-For"] = ip
            base_payload["request_headers"]["X-Real-IP"] = ip
            base_payload["request_body"] = {
                "username": "admin",
                "password": "password123"
            }
            base_payload["request_path"] = "/api/admin/login"
            
            self.send_attack(base_payload, f"malicious_ip_{i}")
            time.sleep(0.5)

    def suspicious_user_agent_attack(self):
        """Simulate attacks with suspicious user agents."""
        print("\n=== SUSPICIOUS USER AGENT ATTACKS ===")
        for i, user_agent in enumerate(SUSPICIOUS_USER_AGENTS, 1):
            base_payload = self.create_base_payload("suspicious_user_agent")
            base_payload["request_headers"]["User-Agent"] = user_agent
            base_payload["request_body"] = {
                "scan": "true",
                "probe": "true"
            }
            base_payload["request_path"] = "/api/scan"
            
            self.send_attack(base_payload, f"suspicious_user_agent_{i}")
            time.sleep(0.5)

    def test_threat_intelligence_endpoints(self):
        """Test the threat intelligence endpoints directly."""
        print("\n=== TESTING THREAT INTELLIGENCE ENDPOINTS ===")
        
        # Test IP reputation
        print("\n--- IP Reputation Tests ---")
        for ip in MALICIOUS_IPS[:3]:  # Test first 3 IPs
            try:
                response = requests.post(
                    f"{self.target_url}/threat-intelligence/ip-reputation",
                    json={"ip": ip},
                    headers=self.headers,
                    timeout=5
                )
                if response.status_code == 200:
                    result = response.json()
                    print(f"IP {ip}: Score={result.get('threat_score', 0)}, Malicious={result.get('is_malicious', False)}")
                else:
                    print(f"IP {ip}: Error {response.status_code}")
            except Exception as e:
                print(f"IP {ip}: Error - {str(e)}")
            time.sleep(0.5)

        # Test domain reputation
        print("\n--- Domain Reputation Tests ---")
        for domain in MALICIOUS_DOMAINS[:3]:  # Test first 3 domains
            try:
                response = requests.post(
                    f"{self.target_url}/threat-intelligence/domain-reputation",
                    json={"domain": domain},
                    headers=self.headers,
                    timeout=5
                )
                if response.status_code == 200:
                    result = response.json()
                    print(f"Domain {domain}: Score={result.get('threat_score', 0)}, Malicious={result.get('is_malicious', False)}")
                else:
                    print(f"Domain {domain}: Error {response.status_code}")
            except Exception as e:
                print(f"Domain {domain}: Error - {str(e)}")
            time.sleep(0.5)

        # Test YARA rule matching
        print("\n--- YARA Rule Matching Tests ---")
        yara_test_content = [
            "GET /admin?cmd=whoami HTTP/1.1",
            "<script>alert('xss')</script>",
            "'; DROP TABLE users --",
            "../../../etc/passwd"
        ]
        
        for content in yara_test_content:
            try:
                response = requests.post(
                    f"{self.target_url}/threat-intelligence/yara-match",
                    json={"content": content},
                    headers=self.headers,
                    timeout=5
                )
                if response.status_code == 200:
                    result = response.json()
                    print(f"Content '{content[:30]}...': Suspicious={result.get('is_suspicious', False)}, Matches={result.get('total_matches', 0)}")
                else:
                    print(f"Content '{content[:30]}...': Error {response.status_code}")
            except Exception as e:
                print(f"Content '{content[:30]}...': Error - {str(e)}")
            time.sleep(0.5)

    def test_analytics_endpoints(self):
        """Test the analytics endpoints."""
        print("\n=== TESTING ANALYTICS ENDPOINTS ===")
        
        analytics_endpoints = [
            "/incidents/analytics/overview",
            "/incidents/analytics/attack-distribution",
            "/incidents/analytics/severity",
            "/incidents/analytics/geo",
            "/incidents/analytics/system-impact"
        ]
        
        for endpoint in analytics_endpoints:
            try:
                response = requests.get(
                    f"{self.target_url}{endpoint}",
                    headers=self.headers,
                    timeout=5
                )
                if response.status_code == 200:
                    result = response.json()
                    print(f"{endpoint}: Success - {len(result)} fields returned")
                else:
                    print(f"{endpoint}: Error {response.status_code}")
            except Exception as e:
                print(f"{endpoint}: Error - {str(e)}")
            time.sleep(0.5)

    def run_comprehensive_attack_sequence(self):
        """Run a comprehensive sequence of different attacks."""
        print("Starting comprehensive attack simulation...")
        print("=" * 60)
        
        # Test threat intelligence endpoints first
        self.test_threat_intelligence_endpoints()
        
        # Run different types of attacks
        self.sql_injection_attack()
        self.xss_attack()
        self.path_traversal_attack()
        self.command_injection_attack()
        self.nosql_injection_attack()
        self.malicious_ip_attack()
        self.suspicious_user_agent_attack()
        
        # Test analytics endpoints
        self.test_analytics_endpoints()
        
        print("\n" + "=" * 60)
        print("Comprehensive attack simulation completed.")

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description='Enhanced security attack simulation tool')
    parser.add_argument('--target', required=True, help='Target URL')
    parser.add_argument('--api-key', required=True, help='API key for authentication')
    parser.add_argument('--interval', type=float, default=0.5, help='Interval between requests in seconds')
    parser.add_argument('--test-type', choices=['all', 'attacks', 'threat-intel', 'analytics'], 
                       default='all', help='Type of tests to run')
    
    args = parser.parse_args()
    
    simulator = AttackSimulator(args.target, args.api_key)
    
    if args.test_type == 'all':
        simulator.run_comprehensive_attack_sequence()
    elif args.test_type == 'attacks':
        simulator.sql_injection_attack()
        simulator.xss_attack()
        simulator.path_traversal_attack()
        simulator.command_injection_attack()
        simulator.nosql_injection_attack()
        simulator.malicious_ip_attack()
        simulator.suspicious_user_agent_attack()
    elif args.test_type == 'threat-intel':
        simulator.test_threat_intelligence_endpoints()
    elif args.test_type == 'analytics':
        simulator.test_analytics_endpoints()

if __name__ == '__main__':
    main() 