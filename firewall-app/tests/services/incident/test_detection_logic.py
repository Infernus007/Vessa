
import pytest
from unittest.mock import MagicMock, AsyncMock
from services.incident.core.incident_service import IncidentService
from services.incident.core.scoring import ThreatScore, ThreatType

@pytest.fixture
def mock_db():
    return MagicMock()

@pytest.fixture
def service(mock_db):
    return IncidentService(mock_db)

def test_static_analysis_sql_injection(service):
    """Test SQL injection detection."""
    # Test basic SQL injection
    result = service._perform_basic_static_analysis(
        source_ip="127.0.0.1",
        request_path="/api/users",
        request_method="GET",
        query_params={"id": "1' OR '1'='1"}
    )
    
    assert result["threat_score"] >= ThreatScore.SQL_INJECTION
    assert result["threat_type"] == ThreatType.SQL_INJECTION
    assert result["should_block"] is True
    assert "SQL injection pattern detected" in result["findings"][0]

def test_static_analysis_xss(service):
    """Test XSS detection."""
    # Test basic XSS
    result = service._perform_basic_static_analysis(
        source_ip="127.0.0.1",
        request_path="/api/comments",
        request_method="POST",
        body={"content": "<script>alert('xss')</script>"}
    )
    
    assert result["threat_score"] >= ThreatScore.XSS
    assert result["threat_type"] == ThreatType.XSS
    assert result["should_block"] is True
    assert "XSS pattern detected" in result["findings"][0]

def test_static_analysis_safe_request(service):
    """Test safe request."""
    result = service._perform_basic_static_analysis(
        source_ip="127.0.0.1",
        request_path="/api/users",
        request_method="GET",
        query_params={"id": "123"}
    )
    
    assert result["threat_score"] == 0.0
    assert result["threat_type"] == ThreatType.SAFE
    assert result["should_block"] is False
    assert len(result["findings"]) == 0

def test_static_analysis_suspicious_user_agent(service):
    """Test suspicious user agent detection."""
    result = service._perform_basic_static_analysis(
        source_ip="127.0.0.1",
        request_path="/api/users",
        request_method="GET",
        headers={"User-Agent": "sqlmap/1.0"}
    )
    
    # Should be suspicious but maybe not blocked solely on UA depending on threshold
    # Threshold is 0.5, SUSPICIOUS_USER_AGENT is 0.2
    assert result["threat_score"] >= ThreatScore.SUSPICIOUS_USER_AGENT
    assert result["should_block"] is False 
    assert "Suspicious user agent detected" in result["findings"][0]

def test_static_analysis_combined_threats(service):
    """Test combined threats (UA + SQLi)."""
    result = service._perform_basic_static_analysis(
        source_ip="127.0.0.1",
        request_path="/api/users",
        request_method="GET",
        headers={"User-Agent": "sqlmap/1.0"},
        query_params={"id": "1' OR '1'='1"}
    )
    
    # Should be blocked
    assert result["threat_score"] >= ThreatScore.SQL_INJECTION
    assert result["should_block"] is True
