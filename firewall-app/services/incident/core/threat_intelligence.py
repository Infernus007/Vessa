"""
Threat Intelligence Service

This module provides threat intelligence capabilities including:
- YARA signature matching
- Threat feed integration
- IP/domain reputation checking
- IOC (Indicators of Compromise) detection
"""

import requests
import json
import re
import hashlib
import ipaddress
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
import asyncio
import aiohttp
from dataclasses import dataclass
from urllib.parse import urlparse
import logging

logger = logging.getLogger(__name__)

# Global flag for YARA availability
YARA_AVAILABLE = False
yara = None

@dataclass
class ThreatFeed:
    """Represents a threat feed configuration."""
    name: str
    url: str
    type: str  # 'ip', 'domain', 'url', 'hash'
    format: str  # 'json', 'csv', 'txt'
    update_interval: int  # hours
    last_update: Optional[datetime] = None
    data: Optional[List[str]] = None

@dataclass
class YARARule:
    """Represents a YARA rule configuration."""
    name: str
    rule_content: str
    category: str
    severity: str
    description: str
    enabled: bool = True

class ThreatIntelligenceService:
    """Service for threat intelligence and YARA signature matching."""
    
    def __init__(self, cache_dir: str = "/tmp/threat_intel_cache"):
        """Initialize the threat intelligence service.
        
        Args:
            cache_dir: Directory to cache threat feed data
        """
        global YARA_AVAILABLE, yara
        
        self.cache_dir = cache_dir
        self.yara_rules: Dict[str, Any] = {}  # Changed from yara.Rule to Any
        self.threat_feeds: Dict[str, ThreatFeed] = {}
        self.reputation_cache: Dict[str, Dict[str, Any]] = {}
        self.cache_ttl = 3600  # 1 hour cache TTL
        
        # Try to import yara, but make it optional
        if not YARA_AVAILABLE:
            try:
                import yara
                YARA_AVAILABLE = True
                print("[INFO] YARA library imported successfully")
            except (ImportError, OSError) as e:
                YARA_AVAILABLE = False
                print(f"[WARNING] YARA library not available: {e}")
                yara = None
        
        # Initialize threat feeds
        self._initialize_threat_feeds()
        
        # Initialize YARA rules only if available
        if YARA_AVAILABLE:
            self._initialize_yara_rules()
        else:
            print("[WARNING] YARA rules initialization skipped - YARA not available")
        
        # API keys for external services (should be in environment variables)
        self.virustotal_api_key = None  # os.getenv("VIRUSTOTAL_API_KEY")
        self.abuseipdb_api_key = None   # os.getenv("ABUSEIPDB_API_KEY")
        self.shodan_api_key = None      # os.getenv("SHODAN_API_KEY")
        
    def _initialize_threat_feeds(self):
        """Initialize default threat feeds."""
        self.threat_feeds = {
            "abuseipdb": ThreatFeed(
                name="AbuseIPDB",
                url="https://api.abuseipdb.com/api/v2/blacklist",
                type="ip",
                format="json",
                update_interval=24
            ),
            "tor_exit_nodes": ThreatFeed(
                name="Tor Exit Nodes",
                url="https://check.torproject.org/exit-addresses",
                type="ip",
                format="txt",
                update_interval=6
            ),
            "malware_bazaar": ThreatFeed(
                name="Malware Bazaar",
                url="https://bazaar.abuse.ch/export/txt/recent/",
                type="hash",
                format="txt",
                update_interval=12
            ),
            "phishing_database": ThreatFeed(
                name="Phishing Database",
                url="https://openphish.com/feed.txt",
                type="url",
                format="txt",
                update_interval=1
            )
        }
    
    def _initialize_yara_rules(self):
        """Initialize YARA rules for various attack patterns."""
        if not YARA_AVAILABLE:
            print("[WARNING] Cannot initialize YARA rules - YARA not available")
            return
            
        yara_rules_content = {
            "sql_injection": r"""
rule SQL_Injection_Attack {
    meta:
        description = "Detects SQL injection patterns in HTTP requests"
        severity = "high"
        category = "injection"
    
    strings:
        $union = "union" nocase
        $select = "select" nocase
        $insert = "insert" nocase
        $delete = "delete" nocase
        $drop = "drop" nocase
        $update = "update" nocase
        $or_1_1 = "or 1=1" nocase
        $or_true = "or true" nocase
        $comment = /--|#|\/\*/
        $semicolon = ";"
        $quote = /'|"|`/
        
    condition:
        any of ($union, $select, $insert, $delete, $drop, $update) and
        any of ($or_1_1, $or_true, $comment, $semicolon, $quote)
}
""",
            "xss_attack": r"""
rule XSS_Attack {
    meta:
        description = "Detects XSS (Cross-Site Scripting) patterns"
        severity = "high"
        category = "xss"
    
    strings:
        $script_tag = /<script[^>]*>/i
        $javascript = "javascript:" nocase
        $onload = "onload" nocase
        $onerror = "onerror" nocase
        $onclick = "onclick" nocase
        $eval = "eval(" nocase
        $alert = "alert(" nocase
        $confirm = "confirm(" nocase
        $prompt = "prompt(" nocase
        
    condition:
        any of ($script_tag, $javascript, $onload, $onerror, $onclick) or
        any of ($eval, $alert, $confirm, $prompt)
}
""",
            "path_traversal": r"""
rule Path_Traversal {
    meta:
        description = "Detects path traversal attempts"
        severity = "high"
        category = "path_traversal"
    
    strings:
        $dot_dot = ".."
        $passwd = "/etc/passwd" nocase
        $shadow = "/etc/shadow" nocase
        $hosts = "/etc/hosts" nocase
        $windows = /c:\\windows|windows\\system32/i
        $backup = /\.(bak|old|backup|tmp)$/i
        
    condition:
        $dot_dot and any of ($passwd, $shadow, $hosts, $windows, $backup)
}
""",
            "command_injection": r"""
rule Command_Injection {
    meta:
        description = "Detects command injection patterns"
        severity = "critical"
        category = "command_injection"
    
    strings:
        $pipe = "|"
        $semicolon = ";"
        $backtick = "`"
        $dollar = "$("
        $bash = "bash" nocase
        $sh = "sh" nocase
        $cmd = "cmd" nocase
        $powershell = "powershell" nocase
        $ping = "ping" nocase
        $nc = "nc" nocase
        $netcat = "netcat" nocase
        
    condition:
        any of ($pipe, $semicolon, $backtick, $dollar) and
        any of ($bash, $sh, $cmd, $powershell, $ping, $nc, $netcat)
}
""",
            "file_upload": r"""
rule Malicious_File_Upload {
    meta:
        description = "Detects malicious file upload attempts"
        severity = "high"
        category = "file_upload"
    
    strings:
        $php = /\.php[0-9]*$/i
        $asp = /\.asp$/i
        $jsp = /\.jsp$/i
        $exe = /\.exe$/i
        $bat = /\.bat$/i
        $cmd = /\.cmd$/i
        $ps1 = /\.ps1$/i
        $sh = /\.sh$/i
        
    condition:
        any of ($php, $asp, $jsp, $exe, $bat, $cmd, $ps1, $sh)
}
""",
            "lfi_attack": r"""
rule LFI_Attack {
    meta:
        description = "Detects Local File Inclusion attempts"
        severity = "high"
        category = "lfi"
    
    strings:
        $include = "include" nocase
        $require = "require" nocase
        $file_get = "file_get_contents" nocase
        $readfile = "readfile" nocase
        $fopen = "fopen" nocase
        $file = "file://" nocase
        $php_wrapper = "php://" nocase
        $data_wrapper = "data://" nocase
        
    condition:
        any of ($include, $require, $file_get, $readfile, $fopen) and
        any of ($file, $php_wrapper, $data_wrapper)
}
""",
            "ssrf_attack": r"""
rule SSRF_Attack {
    meta:
        description = "Detects Server-Side Request Forgery attempts"
        severity = "high"
        category = "ssrf"
    
    strings:
        $http = "http://" nocase
        $https = "https://" nocase
        $file = "file://" nocase
        $ftp = "ftp://" nocase
        $gopher = "gopher://" nocase
        $dict = "dict://" nocase
        $ldap = "ldap://" nocase
        $tftp = "tftp://" nocase
        $internal_ip = /(127\.0\.0\.1|localhost|0\.0\.0\.0|10\.|172\.(1[6-9]|2[0-9]|3[01])\.|192\.168\.)/i
        $aws_metadata = "169.254.169.254" nocase
        $gcp_metadata = "metadata.google.internal" nocase
        $azure_metadata = "169.254.169.254" nocase
        
    condition:
        any of ($http, $https, $file, $ftp, $gopher, $dict, $ldap, $tftp) and
        any of ($internal_ip, $aws_metadata, $gcp_metadata, $azure_metadata)
}
"""
        }
        
        # Compile YARA rules
        for rule_name, rule_content in yara_rules_content.items():
            try:
                self.yara_rules[rule_name] = yara.compile(source=rule_content)
                logger.info(f"Loaded YARA rule: {rule_name}")
            except Exception as e:
                logger.error(f"Failed to load YARA rule {rule_name}: {e}")
    
    async def analyze_request_with_yara(
        self,
        method: str,
        url: str,
        path: str,
        headers: Dict[str, str],
        body: Optional[Any] = None,
        query_params: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """Analyze request using YARA signatures.
        
        Args:
            method: HTTP method
            url: Full URL
            path: Request path
            headers: Request headers
            body: Request body
            query_params: Query parameters
            
        Returns:
            Dictionary containing YARA analysis results
        """
        if not YARA_AVAILABLE:
            return {
                "yara_matches": [],
                "threat_score": 0,
                "matched_rules": [],
                "severity": "low",
                "error": "YARA not available"
            }
        
        # Format request data for YARA analysis
        request_data = self._format_request_for_yara(
            method, url, path, headers, body, query_params
        )
        
        matches = []
        threat_score = 0
        
        # Run YARA rules against the request data
        for rule_name, rule in self.yara_rules.items():
            try:
                rule_matches = rule.match(data=request_data.encode('utf-8'))
                if rule_matches:
                    for match in rule_matches:
                        match_info = {
                            "rule": rule_name,
                            "strings": [str(s) for s in match.strings],
                            "meta": match.meta,
                            "offset": match.offset,
                            "matched_data": match.matched_data.decode('utf-8', errors='ignore')
                        }
                        matches.append(match_info)
                        
                        # Add to threat score based on severity
                        severity = match.meta.get('severity', 'medium')
                        if severity == 'critical':
                            threat_score += 100
                        elif severity == 'high':
                            threat_score += 75
                        elif severity == 'medium':
                            threat_score += 50
                        elif severity == 'low':
                            threat_score += 25
                            
            except Exception as e:
                logger.error(f"Error running YARA rule {rule_name}: {e}")
        
        return {
            "yara_matches": matches,
            "threat_score": min(threat_score, 100),
            "matched_rules": [m["rule"] for m in matches],
            "severity": "critical" if threat_score >= 100 else "high" if threat_score >= 75 else "medium" if threat_score >= 50 else "low"
        }
    
    def _format_request_for_yara(
        self,
        method: str,
        url: str,
        path: str,
        headers: Dict[str, str],
        body: Optional[Any],
        query_params: Optional[Dict[str, str]]
    ) -> str:
        """Format request data for YARA analysis."""
        formatted = f"{method} {path}"
        
        # Add query parameters
        if query_params:
            query_string = "&".join([f"{k}={v}" for k, v in query_params.items()])
            formatted += f"?{query_string}"
        
        formatted += "\n"
        
        # Add headers
        for key, value in headers.items():
            formatted += f"{key}: {value}\n"
        
        # Add body
        if body:
            formatted += "\n"
            if isinstance(body, dict):
                formatted += json.dumps(body)
            else:
                formatted += str(body)
        
        return formatted
    
    async def check_ip_reputation(self, ip: str) -> Dict[str, Any]:
        """Check IP reputation using multiple sources.
        
        Args:
            ip: IP address to check
            
        Returns:
            Dictionary containing reputation information
        """
        # Check cache first
        cache_key = f"ip_reputation_{ip}"
        if cache_key in self.reputation_cache:
            cached_data = self.reputation_cache[cache_key]
            if datetime.now() - cached_data["timestamp"] < timedelta(seconds=self.cache_ttl):
                return cached_data["data"]
        
        reputation_data = {
            "ip": ip,
            "is_malicious": False,
            "confidence": 0,
            "categories": [],
            "sources": [],
            "last_seen": None,
            "abuse_confidence": 0
        }
        
        try:
            # Check if IP is private
            ip_obj = ipaddress.ip_address(ip)
            if ip_obj.is_private:
                reputation_data["categories"].append("private_ip")
                reputation_data["confidence"] = 0
                return reputation_data
            
            # Check AbuseIPDB (if API key available)
            if self.abuseipdb_api_key:
                abuse_data = await self._check_abuseipdb(ip)
                if abuse_data:
                    reputation_data.update(abuse_data)
            
            # Check local threat feeds
            feed_matches = await self._check_threat_feeds(ip, "ip")
            if feed_matches:
                reputation_data["is_malicious"] = True
                reputation_data["confidence"] = max(reputation_data["confidence"], 75)
                reputation_data["categories"].extend(feed_matches)
                reputation_data["sources"].append("threat_feeds")
            
            # Check if it's a Tor exit node
            if await self._is_tor_exit_node(ip):
                reputation_data["is_malicious"] = True
                reputation_data["confidence"] = max(reputation_data["confidence"], 60)
                reputation_data["categories"].append("tor_exit_node")
                reputation_data["sources"].append("tor_project")
            
            # Cache the result
            self.reputation_cache[cache_key] = {
                "data": reputation_data,
                "timestamp": datetime.now()
            }
            
        except Exception as e:
            logger.error(f"Error checking IP reputation for {ip}: {e}")
        
        return reputation_data
    
    async def check_domain_reputation(self, domain: str) -> Dict[str, Any]:
        """Check domain reputation.
        
        Args:
            domain: Domain to check
            
        Returns:
            Dictionary containing reputation information
        """
        cache_key = f"domain_reputation_{domain}"
        if cache_key in self.reputation_cache:
            cached_data = self.reputation_cache[cache_key]
            if datetime.now() - cached_data["timestamp"] < timedelta(seconds=self.cache_ttl):
                return cached_data["data"]
        
        reputation_data = {
            "domain": domain,
            "is_malicious": False,
            "confidence": 0,
            "categories": [],
            "sources": [],
            "registration_date": None,
            "expiration_date": None
        }
        
        try:
            # Check threat feeds
            feed_matches = await self._check_threat_feeds(domain, "domain")
            if feed_matches:
                reputation_data["is_malicious"] = True
                reputation_data["confidence"] = max(reputation_data["confidence"], 75)
                reputation_data["categories"].extend(feed_matches)
                reputation_data["sources"].append("threat_feeds")
            
            # Check VirusTotal (if API key available)
            if self.virustotal_api_key:
                vt_data = await self._check_virustotal_domain(domain)
                if vt_data:
                    reputation_data.update(vt_data)
            
            # Cache the result
            self.reputation_cache[cache_key] = {
                "data": reputation_data,
                "timestamp": datetime.now()
            }
            
        except Exception as e:
            logger.error(f"Error checking domain reputation for {domain}: {e}")
        
        return reputation_data
    
    async def check_url_reputation(self, url: str) -> Dict[str, Any]:
        """Check URL reputation.
        
        Args:
            url: URL to check
            
        Returns:
            Dictionary containing reputation information
        """
        cache_key = f"url_reputation_{hashlib.md5(url.encode()).hexdigest()}"
        if cache_key in self.reputation_cache:
            cached_data = self.reputation_cache[cache_key]
            if datetime.now() - cached_data["timestamp"] < timedelta(seconds=self.cache_ttl):
                return cached_data["data"]
        
        reputation_data = {
            "url": url,
            "is_malicious": False,
            "confidence": 0,
            "categories": [],
            "sources": [],
            "domain": None
        }
        
        try:
            # Extract domain from URL
            parsed_url = urlparse(url)
            domain = parsed_url.netloc
            reputation_data["domain"] = domain
            
            # Check domain reputation
            domain_reputation = await self.check_domain_reputation(domain)
            if domain_reputation["is_malicious"]:
                reputation_data["is_malicious"] = True
                reputation_data["confidence"] = max(reputation_data["confidence"], domain_reputation["confidence"])
                reputation_data["categories"].extend(domain_reputation["categories"])
                reputation_data["sources"].extend(domain_reputation["sources"])
            
            # Check URL-specific threat feeds
            feed_matches = await self._check_threat_feeds(url, "url")
            if feed_matches:
                reputation_data["is_malicious"] = True
                reputation_data["confidence"] = max(reputation_data["confidence"], 75)
                reputation_data["categories"].extend(feed_matches)
                reputation_data["sources"].append("threat_feeds")
            
            # Cache the result
            self.reputation_cache[cache_key] = {
                "data": reputation_data,
                "timestamp": datetime.now()
            }
            
        except Exception as e:
            logger.error(f"Error checking URL reputation for {url}: {e}")
        
        return reputation_data
    
    async def _check_threat_feeds(self, indicator: str, feed_type: str) -> List[str]:
        """Check indicator against threat feeds.
        
        Args:
            indicator: Indicator to check
            feed_type: Type of indicator (ip, domain, url, hash)
            
        Returns:
            List of matched categories
        """
        matches = []
        
        for feed_name, feed in self.threat_feeds.items():
            if feed.type != feed_type:
                continue
            
            # Check if feed needs updating
            if (feed.last_update is None or 
                datetime.now() - feed.last_update > timedelta(hours=feed.update_interval)):
                await self._update_threat_feed(feed)
            
            # Check if indicator is in feed
            if feed.data and indicator in feed.data:
                matches.append(feed_name)
        
        return matches
    
    async def _update_threat_feed(self, feed: ThreatFeed):
        """Update threat feed data.
        
        Args:
            feed: Threat feed to update
        """
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(feed.url) as response:
                    if response.status == 200:
                        content = await response.text()
                        
                        if feed.format == "json":
                            data = json.loads(content)
                            # Handle different JSON formats
                            if isinstance(data, list):
                                feed.data = data
                            elif isinstance(data, dict) and "data" in data:
                                feed.data = data["data"]
                            else:
                                feed.data = []
                        else:
                            # Handle text-based feeds
                            feed.data = [line.strip() for line in content.split('\n') if line.strip()]
                        
                        feed.last_update = datetime.now()
                        logger.info(f"Updated threat feed: {feed.name}")
                    else:
                        logger.warning(f"Failed to update threat feed {feed.name}: {response.status}")
                        
        except Exception as e:
            logger.error(f"Error updating threat feed {feed.name}: {e}")
    
    async def _check_abuseipdb(self, ip: str) -> Optional[Dict[str, Any]]:
        """Check IP against AbuseIPDB.
        
        Args:
            ip: IP address to check
            
        Returns:
            AbuseIPDB data or None
        """
        if not self.abuseipdb_api_key:
            return None
        
        try:
            url = "https://api.abuseipdb.com/api/v2/check"
            params = {
                "ipAddress": ip,
                "maxAgeInDays": 90
            }
            headers = {
                "Accept": "application/json",
                "Key": self.abuseipdb_api_key
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params, headers=headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        result = data.get("data", {})
                        
                        return {
                            "is_malicious": result.get("abuseConfidenceScore", 0) > 25,
                            "confidence": result.get("abuseConfidenceScore", 0),
                            "categories": result.get("reports", []),
                            "sources": ["abuseipdb"],
                            "last_seen": result.get("lastReportedAt")
                        }
                        
        except Exception as e:
            logger.error(f"Error checking AbuseIPDB for {ip}: {e}")
        
        return None
    
    async def _check_virustotal_domain(self, domain: str) -> Optional[Dict[str, Any]]:
        """Check domain against VirusTotal.
        
        Args:
            domain: Domain to check
            
        Returns:
            VirusTotal data or None
        """
        if not self.virustotal_api_key:
            return None
        
        try:
            url = f"https://www.virustotal.com/vtapi/v2/domain/report"
            params = {
                "apikey": self.virustotal_api_key,
                "domain": domain
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        positives = data.get("positives", 0)
                        total = data.get("total", 0)
                        confidence = (positives / total * 100) if total > 0 else 0
                        
                        return {
                            "is_malicious": positives > 0,
                            "confidence": confidence,
                            "categories": data.get("categories", []),
                            "sources": ["virustotal"],
                            "detection_ratio": f"{positives}/{total}"
                        }
                        
        except Exception as e:
            logger.error(f"Error checking VirusTotal for {domain}: {e}")
        
        return None
    
    async def _is_tor_exit_node(self, ip: str) -> bool:
        """Check if IP is a Tor exit node.
        
        Args:
            ip: IP address to check
            
        Returns:
            True if IP is a Tor exit node
        """
        # Check against Tor exit nodes feed
        feed = self.threat_feeds.get("tor_exit_nodes")
        if feed and feed.data:
            return ip in feed.data
        
        return False
    
    async def extract_iocs_from_request(
        self,
        method: str,
        url: str,
        path: str,
        headers: Dict[str, str],
        body: Optional[Any] = None,
        query_params: Optional[Dict[str, str]] = None
    ) -> Dict[str, List[str]]:
        """Extract Indicators of Compromise (IOCs) from request.
        
        Args:
            method: HTTP method
            url: Full URL
            path: Request path
            headers: Request headers
            body: Request body
            query_params: Query parameters
            
        Returns:
            Dictionary containing extracted IOCs
        """
        iocs = {
            "ips": [],
            "domains": [],
            "urls": [],
            "hashes": [],
            "emails": [],
            "file_paths": []
        }
        
        # Extract IPs
        ip_pattern = r'\b(?:\d{1,3}\.){3}\d{1,3}\b'
        all_text = f"{method} {url} {path} {str(headers)} {str(body)} {str(query_params)}"
        
        for match in re.finditer(ip_pattern, all_text):
            ip = match.group()
            try:
                ipaddress.ip_address(ip)  # Validate IP
                iocs["ips"].append(ip)
            except ValueError:
                pass
        
        # Extract domains
        domain_pattern = r'\b(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,}\b'
        for match in re.finditer(domain_pattern, all_text):
            domain = match.group()
            if not domain.startswith(('127.', '192.168.', '10.', '172.')):  # Exclude private IPs
                iocs["domains"].append(domain)
        
        # Extract URLs
        url_pattern = r'https?://[^\s<>"{}|\\^`\[\]]+'
        for match in re.finditer(url_pattern, all_text):
            iocs["urls"].append(match.group())
        
        # Extract MD5 hashes
        md5_pattern = r'\b[a-fA-F0-9]{32}\b'
        for match in re.finditer(md5_pattern, all_text):
            iocs["hashes"].append(match.group())
        
        # Extract SHA1 hashes
        sha1_pattern = r'\b[a-fA-F0-9]{40}\b'
        for match in re.finditer(sha1_pattern, all_text):
            iocs["hashes"].append(match.group())
        
        # Extract SHA256 hashes
        sha256_pattern = r'\b[a-fA-F0-9]{64}\b'
        for match in re.finditer(sha256_pattern, all_text):
            iocs["hashes"].append(match.group())
        
        # Extract emails
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        for match in re.finditer(email_pattern, all_text):
            iocs["emails"].append(match.group())
        
        # Extract file paths
        file_path_pattern = r'[\/\\][^\/\\\s<>"{}|]*\.(?:exe|dll|bat|cmd|ps1|sh|php|asp|jsp|py|js|vbs|jar|war|ear|apk|ipa|deb|rpm|msi|pkg|app|dmg|iso|img|tar|gz|zip|rar|7z|pdf|doc|docx|xls|xlsx|ppt|pptx|txt|log|conf|config|ini|xml|json|yaml|yml|sql|bak|old|backup|tmp|temp)\b'
        for match in re.finditer(file_path_pattern, all_text, re.IGNORECASE):
            iocs["file_paths"].append(match.group())
        
        # Remove duplicates
        for key in iocs:
            iocs[key] = list(set(iocs[key]))
        
        return iocs
    
    async def comprehensive_threat_analysis(
        self,
        method: str,
        url: str,
        path: str,
        headers: Dict[str, str],
        body: Optional[Any] = None,
        query_params: Optional[Dict[str, str]] = None,
        client_ip: Optional[str] = None
    ) -> Dict[str, Any]:
        """Perform comprehensive threat analysis using all available methods.
        
        Args:
            method: HTTP method
            url: Full URL
            path: Request path
            headers: Request headers
            body: Request body
            query_params: Query parameters
            client_ip: Client IP address
            
        Returns:
            Comprehensive threat analysis results
        """
        results = {
            "yara_analysis": {},
            "reputation_checks": {},
            "ioc_extraction": {},
            "overall_threat_score": 0,
            "threat_indicators": [],
            "recommendations": []
        }
        
        # YARA signature analysis
        yara_results = await self.analyze_request_with_yara(
            method, url, path, headers, body, query_params
        )
        results["yara_analysis"] = yara_results
        
        if yara_results["yara_matches"]:
            results["overall_threat_score"] += yara_results["threat_score"]
            results["threat_indicators"].extend([
                f"YARA rule match: {match['rule']}" for match in yara_results["yara_matches"]
            ])
        
        # Extract IOCs
        iocs = await self.extract_iocs_from_request(
            method, url, path, headers, body, query_params
        )
        results["ioc_extraction"] = iocs
        
        # Check reputation for extracted IOCs
        reputation_checks = {}
        
        # Check IP reputation
        for ip in iocs["ips"]:
            if ip != client_ip:  # Don't check client IP unless it's suspicious
                reputation = await self.check_ip_reputation(ip)
                reputation_checks[f"ip_{ip}"] = reputation
                if reputation["is_malicious"]:
                    results["overall_threat_score"] += reputation["confidence"]
                    results["threat_indicators"].append(f"Malicious IP: {ip}")
        
        # Check domain reputation
        for domain in iocs["domains"]:
            reputation = await self.check_domain_reputation(domain)
            reputation_checks[f"domain_{domain}"] = reputation
            if reputation["is_malicious"]:
                results["overall_threat_score"] += reputation["confidence"]
                results["threat_indicators"].append(f"Malicious domain: {domain}")
        
        # Check URL reputation
        for url_ioc in iocs["urls"]:
            reputation = await self.check_url_reputation(url_ioc)
            reputation_checks[f"url_{hashlib.md5(url_ioc.encode()).hexdigest()}"] = reputation
            if reputation["is_malicious"]:
                results["overall_threat_score"] += reputation["confidence"]
                results["threat_indicators"].append(f"Malicious URL: {url_ioc}")
        
        results["reputation_checks"] = reputation_checks
        
        # Generate recommendations
        if results["overall_threat_score"] >= 75:
            results["recommendations"].append("BLOCK: High threat score detected")
        elif results["overall_threat_score"] >= 50:
            results["recommendations"].append("MONITOR: Medium threat score detected")
        elif results["overall_threat_score"] >= 25:
            results["recommendations"].append("LOG: Low threat score detected")
        
        if yara_results["yara_matches"]:
            results["recommendations"].append("Investigate YARA rule matches")
        
        if any(check["is_malicious"] for check in reputation_checks.values()):
            results["recommendations"].append("Investigate reputation check results")
        
        # Normalize threat score
        results["overall_threat_score"] = min(results["overall_threat_score"], 100)
        
        return results 