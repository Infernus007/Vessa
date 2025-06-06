#!/usr/bin/env python3

import requests
import time
import argparse
import json
from typing import Dict, List
import random
from datetime import datetime

# Attack payloads
SQL_INJECTION_PAYLOADS = [
    "' OR '1'='1",
    "admin' --",
    "' UNION SELECT * FROM users --",
    "'; DROP TABLE users --",
    "' OR 'x'='x",
]

XSS_PAYLOADS = [
    "<script>alert('xss')</script>",
    "<img src=x onerror=alert('xss')>",
    "javascript:alert('xss')",
    "<svg/onload=alert('xss')>",
    "'\\'><script>alert('xss')</script>",
]

PATH_TRAVERSAL_PAYLOADS = [
    "../../../etc/passwd",
    "..\\..\\..\\windows\\system32\\config\\sam",
    "....//....//....//etc/hosts",
    "%2e%2e%2f%2e%2e%2f%2e%2e%2fetc%2fpasswd",
    "..%252f..%252f..%252fetc%252fpasswd"
]

COMMAND_INJECTION_PAYLOADS = [
    "; cat /etc/passwd",
    "| cat /etc/passwd",
    "`cat /etc/passwd`",
    "$(cat /etc/passwd)",
    "&& cat /etc/passwd"
]

class AttackSimulator:
    """Simulates various types of attacks."""

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
                timeout=5
            )
            print(f"Attack sent to {url}")
            print(f"Status: {response.status_code}")
            
            # Print analysis results
            if response.status_code == 200:
                analysis = response.json()
                print(f"Threat Score: {analysis.get('threat_score', 0)}")
                print(f"Threat Type: {analysis.get('threat_type', 'unknown')}")
                print(f"Findings: {analysis.get('findings', [])}")
                if analysis.get('incident_id'):
                    print(f"Incident Created: {analysis['incident_id']}")
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
        for payload in SQL_INJECTION_PAYLOADS:
            base_payload = self.create_base_payload("sql_injection")
            base_payload["request_body"] = {
                "username": payload,
                "password": "' OR '1'='1"
            }
            base_payload["request_query_params"] = {
                "id": "1 OR 1=1"
            }
            
            self.send_attack(base_payload, "sql_injection")
            time.sleep(1)

    def xss_attack(self):
        """Simulate XSS attacks."""
        for payload in XSS_PAYLOADS:
            base_payload = self.create_base_payload("xss")
            base_payload["request_body"] = {
                "comment": payload,
                "user_input": payload
            }
            base_payload["request_headers"]["Referer"] = f"javascript:{payload}"
            
            self.send_attack(base_payload, "xss")
            time.sleep(1)

    def path_traversal_attack(self):
        """Simulate path traversal attacks."""
        for payload in PATH_TRAVERSAL_PAYLOADS:
            base_payload = self.create_base_payload("path_traversal")
            base_payload["request_path"] = f"/api/files/{payload}"
            base_payload["request_query_params"] = {
                "file": payload,
                "path": payload
            }
            
            self.send_attack(base_payload, "path_traversal")
            time.sleep(1)

    def command_injection_attack(self):
        """Simulate command injection attacks."""
        for payload in COMMAND_INJECTION_PAYLOADS:
            base_payload = self.create_base_payload("command_injection")
            base_payload["request_body"] = {
                "command": payload,
                "input": payload
            }
            base_payload["request_query_params"] = {
                "cmd": payload
            }
            
            self.send_attack(base_payload, "command_injection")
            time.sleep(1)

    def run_attack_sequence(self):
        """Run a sequence of different attacks."""
        print("Starting attack simulation...")
        
        # Run different types of attacks
        self.sql_injection_attack()
        self.xss_attack()
        self.path_traversal_attack()
        self.command_injection_attack()
        
        print("Attack simulation completed.")

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description='Security attack simulation tool')
    parser.add_argument('--target', required=True, help='Target URL')
    parser.add_argument('--api-key', required=True, help='API key for authentication')
    parser.add_argument('--interval', type=float, default=1.0, help='Interval between requests in seconds')
    
    args = parser.parse_args()
    
    simulator = AttackSimulator(args.target, args.api_key)
    simulator.run_attack_sequence()

if __name__ == '__main__':
    main() 