"""Threat Intelligence Service.

This module provides threat intelligence capabilities including:
- IP reputation checking
- Domain reputation checking
- URL reputation checking
- YARA rule matching
- Threat feed integration
"""

import asyncio
import aiohttp
import json
import re
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import logging
from urllib.parse import urlparse
import ipaddress

logger = logging.getLogger(__name__)

class ThreatIntelligenceService:
    """Service for threat intelligence gathering and analysis."""
    
    def __init__(self):
        """Initialize the threat intelligence service."""
        self.session = None
        self.cache = {}
        self.cache_ttl = 3600  # 1 hour cache
        
        # YARA rules (simplified for demo)
        self.yara_rules = {
            "malware_patterns": [
                r"(?i)(malware|virus|trojan|backdoor|keylogger)",
                r"(?i)(cmd\.exe|powershell|wscript|cscript)",
                r"(?i)(download|upload|execute|run)",
                r"(?i)(base64|hex|urlencode)",
            ],
            "suspicious_ips": [
                r"^(10\.|172\.(1[6-9]|2[0-9]|3[01])\.|192\.168\.)",  # Private IPs
                r"^(0\.0\.0\.0|127\.0\.0\.1|255\.255\.255\.255)",  # Special IPs
            ]
        }
        
    async def __aenter__(self):
        """Async context manager entry."""
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.session:
            await self.session.close()
            
    async def check_ip_reputation(self, ip: str) -> Dict[str, Any]:
        """Check IP reputation using multiple sources."""
        try:
            # Validate IP
            ipaddress.ip_address(ip)
            
            # Check cache
            cache_key = f"ip_{ip}"
            if cache_key in self.cache:
                cached_data = self.cache[cache_key]
                if datetime.now() - cached_data["timestamp"] < timedelta(seconds=self.cache_ttl):
                    return cached_data["data"]
            
            # Check against threat feeds (simplified)
            reputation_data = {
                "ip": ip,
                "is_malicious": False,
                "threat_score": 0,
                "categories": [],
                "sources": [],
                "last_seen": None,
                "first_seen": None,
                "confidence": 0.0
            }
            
            # Check if it's a private IP
            if ipaddress.ip_address(ip).is_private:
                reputation_data["categories"].append("private_ip")
                reputation_data["threat_score"] += 10
                
            # Check if it's a known malicious IP (demo data)
            malicious_ips = [
                "192.168.1.100",  # Demo malicious IP
                "10.0.0.50",      # Demo malicious IP
            ]
            
            if ip in malicious_ips:
                reputation_data["is_malicious"] = True
                reputation_data["threat_score"] = 90
                reputation_data["categories"].append("malware")
                reputation_data["confidence"] = 0.8
                
            # Cache the result
            self.cache[cache_key] = {
                "data": reputation_data,
                "timestamp": datetime.now()
            }
            
            return reputation_data
            
        except Exception as e:
            logger.error(f"Error checking IP reputation for {ip}: {e}")
            return {
                "ip": ip,
                "is_malicious": False,
                "threat_score": 0,
                "categories": [],
                "sources": [],
                "error": str(e)
            }
            
    async def check_domain_reputation(self, domain: str) -> Dict[str, Any]:
        """Check domain reputation."""
        try:
            # Check cache
            cache_key = f"domain_{domain}"
            if cache_key in self.cache:
                cached_data = self.cache[cache_key]
                if datetime.now() - cached_data["timestamp"] < timedelta(seconds=self.cache_ttl):
                    return cached_data["data"]
            
            reputation_data = {
                "domain": domain,
                "is_malicious": False,
                "threat_score": 0,
                "categories": [],
                "sources": [],
                "registration_date": None,
                "expiration_date": None,
                "confidence": 0.0
            }
            
            # Check for suspicious patterns
            suspicious_patterns = [
                r"(?i)(malware|virus|hack|exploit)",
                r"(?i)(free|download|crack|keygen)",
                r"(?i)(bit\.ly|tinyurl|goo\.gl)",  # URL shorteners
            ]
            
            for pattern in suspicious_patterns:
                if re.search(pattern, domain):
                    reputation_data["threat_score"] += 20
                    reputation_data["categories"].append("suspicious_pattern")
                    
            # Check if it's a known malicious domain (demo data)
            malicious_domains = [
                "malware.example.com",
                "hack.test.com",
            ]
            
            if domain in malicious_domains:
                reputation_data["is_malicious"] = True
                reputation_data["threat_score"] = 85
                reputation_data["categories"].append("malware")
                reputation_data["confidence"] = 0.7
                
            # Cache the result
            self.cache[cache_key] = {
                "data": reputation_data,
                "timestamp": datetime.now()
            }
            
            return reputation_data
            
        except Exception as e:
            logger.error(f"Error checking domain reputation for {domain}: {e}")
            return {
                "domain": domain,
                "is_malicious": False,
                "threat_score": 0,
                "categories": [],
                "sources": [],
                "error": str(e)
            }
            
    async def check_url_reputation(self, url: str) -> Dict[str, Any]:
        """Check URL reputation."""
        try:
            parsed_url = urlparse(url)
            
            # Check cache
            cache_key = f"url_{url}"
            if cache_key in self.cache:
                cached_data = self.cache[cache_key]
                if datetime.now() - cached_data["timestamp"] < timedelta(seconds=self.cache_ttl):
                    return cached_data["data"]
            
            reputation_data = {
                "url": url,
                "is_malicious": False,
                "threat_score": 0,
                "categories": [],
                "sources": [],
                "confidence": 0.0
            }
            
            # Check domain reputation
            domain_reputation = await self.check_domain_reputation(parsed_url.netloc)
            reputation_data["threat_score"] += domain_reputation["threat_score"]
            reputation_data["categories"].extend(domain_reputation["categories"])
            
            # Check URL path for suspicious patterns
            suspicious_paths = [
                r"(?i)(admin|login|wp-admin|phpmyadmin)",
                r"(?i)(\.php|\.asp|\.jsp|\.exe|\.bat)",
                r"(?i)(cmd|shell|exec|system)",
            ]
            
            for pattern in suspicious_paths:
                if re.search(pattern, parsed_url.path):
                    reputation_data["threat_score"] += 15
                    reputation_data["categories"].append("suspicious_path")
                    
            # Check query parameters
            if parsed_url.query:
                query_patterns = [
                    r"(?i)(script|javascript|vbscript)",
                    r"(?i)(union|select|insert|delete)",
                    r"(?i)(cmd|exec|system)",
                ]
                
                for pattern in query_patterns:
                    if re.search(pattern, parsed_url.query):
                        reputation_data["threat_score"] += 25
                        reputation_data["categories"].append("suspicious_query")
                        
            # Determine if malicious
            if reputation_data["threat_score"] >= 50:
                reputation_data["is_malicious"] = True
                reputation_data["confidence"] = min(reputation_data["threat_score"] / 100, 0.9)
                
            # Cache the result
            self.cache[cache_key] = {
                "data": reputation_data,
                "timestamp": datetime.now()
            }
            
            return reputation_data
            
        except Exception as e:
            logger.error(f"Error checking URL reputation for {url}: {e}")
            return {
                "url": url,
                "is_malicious": False,
                "threat_score": 0,
                "categories": [],
                "sources": [],
                "error": str(e)
            }
            
    def match_yara_rules(self, content: str) -> Dict[str, Any]:
        """Match content against YARA rules."""
        matches = []
        
        for rule_name, patterns in self.yara_rules.items():
            for pattern in patterns:
                if re.search(pattern, content):
                    matches.append({
                        "rule_name": rule_name,
                        "pattern": pattern,
                        "matched_text": re.search(pattern, content).group()
                    })
                    
        return {
            "matches": matches,
            "total_matches": len(matches),
            "is_suspicious": len(matches) > 0
        }
        
    async def get_comprehensive_threat_analysis(
        self,
        ip: Optional[str] = None,
        domain: Optional[str] = None,
        url: Optional[str] = None,
        content: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get comprehensive threat analysis for multiple indicators."""
        analysis = {
            "timestamp": datetime.now().isoformat(),
            "indicators": {},
            "overall_threat_score": 0,
            "is_malicious": False,
            "recommendations": [],
            "confidence": 0.0
        }
        
        # Check IP reputation
        if ip:
            analysis["indicators"]["ip"] = await self.check_ip_reputation(ip)
            analysis["overall_threat_score"] += analysis["indicators"]["ip"]["threat_score"]
            
        # Check domain reputation
        if domain:
            analysis["indicators"]["domain"] = await self.check_domain_reputation(domain)
            analysis["overall_threat_score"] += analysis["indicators"]["domain"]["threat_score"]
            
        # Check URL reputation
        if url:
            analysis["indicators"]["url"] = await self.check_url_reputation(url)
            analysis["overall_threat_score"] += analysis["indicators"]["url"]["threat_score"]
            
        # Match YARA rules
        if content:
            analysis["indicators"]["yara"] = self.match_yara_rules(content)
            if analysis["indicators"]["yara"]["is_suspicious"]:
                analysis["overall_threat_score"] += 30
                
        # Determine overall threat level
        analysis["overall_threat_score"] = min(analysis["overall_threat_score"], 100)
        analysis["is_malicious"] = analysis["overall_threat_score"] >= 50
        analysis["confidence"] = min(analysis["overall_threat_score"] / 100, 0.9)
        
        # Generate recommendations
        if analysis["overall_threat_score"] >= 75:
            analysis["recommendations"].append("HIGH: Immediate action required")
        elif analysis["overall_threat_score"] >= 50:
            analysis["recommendations"].append("MEDIUM: Investigation recommended")
        elif analysis["overall_threat_score"] >= 25:
            analysis["recommendations"].append("LOW: Monitor for changes")
            
        return analysis 