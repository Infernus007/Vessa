#!/usr/bin/env python3
"""
Simple script to verify VESSA's core detection logic is working.
Tests SQL injection, XSS, and safe request detection using static analysis.
"""

import asyncio
import sys
import os
from unittest.mock import MagicMock

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), ".")))

from services.incident.core.incident_service import IncidentService
from services.incident.core.scoring import ThreatScore, ThreatType

async def verify_detection():
    """Verify core detection logic works correctly."""
    mock_db = MagicMock()
    # Create service with only static analysis enabled (core pattern-based detection)
    # Note: IncidentService expects int values (1/0), not boolean
    service = IncidentService(mock_db, static_analysis_enabled=1, dynamic_analysis_enabled=0)
    
    print("=" * 60)
    print("VESSA Core Detection Logic Verification")
    print("=" * 60)
    print("Testing pattern-based detection (SQL injection, XSS, etc.)")
    print()
    
    # Test 1: SQL Injection Detection
    print("[TEST 1] SQL Injection Detection")
    print("-" * 60)
    result = await service.analyze_raw_request(
        method="GET",
        url="/api/products/1 UNION SELECT * FROM users",
        path="/api/products/1 UNION SELECT * FROM users",
        headers={"User-Agent": "Mozilla/5.0"}
    )
    print(f"✓ Threat Score: {result['threat_score']:.2f}")
    print(f"✓ Threat Type: {result['threat_type']}")
    print(f"✓ Should Block: {result['should_block']}")
    if result['findings']:
        print(f"✓ Detection: {result['findings'][0]}")
    
    assert result['should_block'] == True, "SQL injection should be blocked!"
    assert result['threat_score'] >= ThreatScore.BLOCKING_THRESHOLD, f"Threat score {result['threat_score']} below threshold {ThreatScore.BLOCKING_THRESHOLD}!"
    print("✅ PASSED\n")
    
    # Test 2: XSS Detection
    print("[TEST 2] XSS Detection")
    print("-" * 60)
    result = await service.analyze_raw_request(
        method="POST",
        url="/api/comments",
        path="/api/comments",
        headers={"User-Agent": "Mozilla/5.0", "Content-Type": "application/json"},
        body={"content": "<script>alert('xss')</script>"}
    )
    print(f"✓ Threat Score: {result['threat_score']:.2f}")
    print(f"✓ Threat Type: {result['threat_type']}")
    print(f"✓ Should Block: {result['should_block']}")
    if result['findings']:
        print(f"✓ Detection: {result['findings'][0]}")
    
    assert result['should_block'] == True, "XSS should be blocked!"
    assert result['threat_score'] >= ThreatScore.BLOCKING_THRESHOLD, f"Threat score {result['threat_score']} below threshold {ThreatScore.BLOCKING_THRESHOLD}!"
    print("✅ PASSED\n")
    
    # Test 3: Command Injection Detection
    print("[TEST 3] Command Injection Detection")
    print("-" * 60)
    result = await service.analyze_raw_request(
        method="POST",
        url="/api/execute",
        path="/api/execute",
        headers={"User-Agent": "Mozilla/5.0"},
        body={"cmd": "ls; rm -rf /"}
    )
    print(f"✓ Threat Score: {result['threat_score']:.2f}")
    print(f"✓ Threat Type: {result['threat_type']}")
    print(f"✓ Should Block: {result['should_block']}")
    if result['findings']:
        print(f"✓ Detection: {result['findings'][0]}")
    
    assert result['should_block'] == True, "Command injection should be blocked!"
    assert result['threat_score'] >= ThreatScore.BLOCKING_THRESHOLD, f"Threat score {result['threat_score']} below threshold {ThreatScore.BLOCKING_THRESHOLD}!"
    print("✅ PASSED\n")
    
    # Test 4: Safe Request
    print("[TEST 4] Safe Request (Should Allow)")
    print("-" * 60)
    result = await service.analyze_raw_request(
        method="GET",
        url="/api/users?id=123",
        path="/api/users",
        headers={"User-Agent": "Mozilla/5.0"},
        query_params={"id": "123"}
    )
    print(f"✓ Threat Score: {result['threat_score']:.2f}")
    print(f"✓ Threat Type: {result['threat_type']}")
    print(f"✓ Should Block: {result['should_block']}")
    
    assert result['should_block'] == False, "Safe request should not be blocked!"
    assert result['threat_score'] < ThreatScore.BLOCKING_THRESHOLD, f"Threat score {result['threat_score']} above threshold {ThreatScore.BLOCKING_THRESHOLD}!"
    print("✅ PASSED\n")
    
    # Summary
    print("=" * 60)
    print("✅ ALL DETECTION TESTS PASSED!")
    print("=" * 60)
    print("\nVESSA's core detection logic is working correctly:")
    print("  ✓ SQL Injection detection")
    print("  ✓ XSS detection")
    print("  ✓ Command Injection detection")
    print("  ✓ Safe request handling")
    print("\nPattern-based detection is operational and ready for deployment.")
    print("=" * 60)

if __name__ == "__main__":
    try:
        asyncio.run(verify_detection())
        sys.exit(0)
    except AssertionError as e:
        print(f"\n❌ VERIFICATION FAILED: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
