# VESSA Attack Simulation Tools

This directory contains comprehensive attack simulation tools to test the VESSA threat detection system, including the enhanced threat intelligence features.

## Overview

The attack simulation tools test:

1. **Static Analysis**: Pattern-based threat detection
2. **ML Analysis**: Machine learning-based threat detection (if enabled)
3. **Threat Intelligence**: IP/domain reputation, YARA rule matching
4. **Analytics**: System analytics and reporting endpoints

## Files

- `attack.py` - Main attack simulation script
- `run_attack_test.py` - Interactive test runner
- `README.md` - This documentation

## Prerequisites

1. VESSA API server running
2. Valid API key
3. Python 3.7+ with required packages:
   ```bash
   pip install requests
   ```

## Quick Start

### Option 1: Interactive Runner (Recommended)

```bash
cd firewall-app/tests/attack-simulation
python run_attack_test.py
```

Follow the prompts to configure your test.

### Option 2: Direct Command Line

```bash
cd firewall-app/tests/attack-simulation
python attack.py --target http://localhost:8000 --api-key YOUR_API_KEY
```

## Test Types

### 1. All Tests (Default)
Tests everything: attacks, threat intelligence, and analytics
```bash
python attack.py --target http://localhost:8000 --api-key YOUR_API_KEY --test-type all
```

### 2. Attack Simulations Only
Tests various attack patterns:
- SQL Injection (10 payloads)
- XSS (10 payloads)
- Path Traversal (10 payloads)
- Command Injection (14 payloads)
- NoSQL Injection (10 payloads)
- Malicious IP attacks (5 IPs)
- Suspicious User Agent attacks (10 UAs)

```bash
python attack.py --target http://localhost:8000 --api-key YOUR_API_KEY --test-type attacks
```

### 3. Threat Intelligence Only
Tests threat intelligence endpoints:
- IP reputation checking
- Domain reputation checking
- YARA rule matching

```bash
python attack.py --target http://localhost:8000 --api-key YOUR_API_KEY --test-type threat-intel
```

### 4. Analytics Only
Tests analytics endpoints:
- Overview analytics
- Attack distribution
- Severity statistics
- Geographic analytics
- System impact analytics

```bash
python attack.py --target http://localhost:8000 --api-key YOUR_API_KEY --test-type analytics
```

## Attack Payloads

### SQL Injection
- Basic SQL injection patterns
- UNION-based attacks
- Error-based attacks
- Blind SQL injection
- Stored procedure attacks

### XSS (Cross-Site Scripting)
- Reflected XSS
- Stored XSS
- DOM-based XSS
- Event handler injection
- JavaScript protocol attacks

### Path Traversal
- Directory traversal sequences
- URL-encoded variants
- Double-encoded variants
- Unicode-encoded variants
- Sensitive file access attempts

### Command Injection
- Shell command injection
- System command execution
- Process injection
- Network scanning attempts

### NoSQL Injection
- MongoDB injection patterns
- JSON-based attacks
- Operator injection
- JavaScript injection

### Malicious IPs
- Known malicious IP addresses
- IPs from threat intelligence feeds
- Suspicious network ranges

### Suspicious User Agents
- Security tool signatures
- Scanner signatures
- Bot signatures
- Malware signatures

## Expected Results

### Threat Detection
- **High Threat Score (75-100)**: Should trigger blocking
- **Medium Threat Score (50-74)**: Should trigger warnings
- **Low Threat Score (25-49)**: Should be logged
- **Safe (0-24)**: Should be allowed

### Analysis Methods
- **Static Analysis**: Pattern matching results
- **ML Analysis**: Machine learning predictions
- **Threat Intelligence**: External threat data

### Incident Creation
- High-threat requests should create incidents
- Incidents should include detailed threat analysis
- Notifications should be sent to stakeholders

## Configuration Options

### Command Line Arguments

```bash
python attack.py --help
```

- `--target`: Target URL (required)
- `--api-key`: API key for authentication (required)
- `--test-type`: Type of test to run (all, attacks, threat-intel, analytics)
- `--interval`: Interval between requests in seconds (default: 0.5)

### Environment Variables

You can also set these environment variables:

```bash
export VESSA_TARGET_URL="http://localhost:8000"
export VESSA_API_KEY="your-api-key"
```

## Example Output

```
Starting comprehensive attack simulation...
============================================================

=== TESTING THREAT INTELLIGENCE ENDPOINTS ===

--- IP Reputation Tests ---
IP 185.220.101.1: Score=85.0, Malicious=True
IP 45.95.147.1: Score=92.0, Malicious=True
IP 185.220.102.1: Score=78.0, Malicious=True

--- Domain Reputation Tests ---
Domain malware.example.com: Score=95.0, Malicious=True
Domain phishing.test.com: Score=88.0, Malicious=True
Domain botnet.suspicious.net: Score=91.0, Malicious=True

--- YARA Rule Matching Tests ---
Content 'GET /admin?cmd=whoami HTTP/1.1': Suspicious=True, Matches=2
Content '<script>alert('xss')</script>': Suspicious=True, Matches=1
Content ''; DROP TABLE users --': Suspicious=True, Matches=1
Content '../../../etc/passwd': Suspicious=True, Matches=1

=== SQL INJECTION ATTACKS ===

[ATTACK] SQL_INJECTION_1 - /api/users?search=' OR '1'='1
Status: 200
Threat Score: 0.85
Threat Type: sql_injection
Should Block: True
Analysis Methods: ['static', 'threat_intelligence']
Findings: 3 findings
  - SQL injection attempt detected
  - Suspicious SQL pattern found in query parameters
  - High confidence threat detected
Incident Created: 123e4567-e89b-12d3-a456-426614174000
Confidence: 0.92

============================================================
Comprehensive attack simulation completed.
```

## Troubleshooting

### Common Issues

1. **Connection Refused**
   - Ensure VESSA API server is running
   - Check target URL and port

2. **Authentication Failed**
   - Verify API key is correct
   - Check API key permissions

3. **Timeout Errors**
   - Increase timeout in attack.py
   - Check network connectivity

4. **No Threats Detected**
   - Verify threat intelligence service is running
   - Check ML models are loaded
   - Review static analysis patterns

### Debug Mode

Enable debug output by modifying the script:

```python
# Add to attack.py
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Security Notes

⚠️ **Important**: These tools are for testing purposes only. Do not use against production systems without proper authorization.

- Only test against your own systems
- Use in isolated environments
- Follow responsible disclosure practices
- Respect rate limits and terms of service

## Contributing

To add new attack patterns:

1. Add payloads to the appropriate payload arrays
2. Create corresponding attack methods
3. Update the main attack sequence
4. Test thoroughly before committing

## Support

For issues or questions:
1. Check the troubleshooting section
2. Review the VESSA documentation
3. Check server logs for errors
4. Verify API endpoint availability 