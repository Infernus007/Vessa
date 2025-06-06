"""Test cases for the incident analysis endpoints."""

import pytest
from fastapi.testclient import TestClient
from datetime import datetime
from main import app

client = TestClient(app)

API_KEY = "vk_2LRb2XnXOfItLBcYBKwByILOHehh5dmenblbNyExWcfw7K"

def test_analyze_request_sql_injection():
    """Test analyzing a SQL injection attack."""
    payload = {
        "request_method": "POST",
        "request_url": "http://example.com/api/users",
        "request_path": "/api/users",
        "request_headers": {
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0",
            "X-Forwarded-For": "192.168.1.100"
        },
        "request_body": {
            "username": "admin' UNION SELECT * FROM users --",
            "password": "' OR 1=1 /*"
        },
        "client_ip": "192.168.1.100",
        "timestamp": datetime.utcnow().isoformat(),
        "service_name": "user-service"
    }

    response = client.post(
        "/incidents/analyze-request",
        json=payload,
        headers={"X-API-Key": API_KEY}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["threat_score"] >= 0.75
    assert data["threat_type"] == "sql_injection"
    assert data["should_block"] == True
    assert len(data["findings"]) > 0

def test_analyze_request_xss():
    """Test analyzing an XSS attack."""
    payload = {
        "request_method": "POST",
        "request_url": "http://example.com/api/comments",
        "request_path": "/api/comments",
        "request_headers": {
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0",
            "X-Forwarded-For": "192.168.1.101"
        },
        "request_body": {
            "comment": "<script>alert('XSS')</script>",
            "user_id": "<img src=x onerror=alert('XSS')>"
        },
        "client_ip": "192.168.1.101",
        "timestamp": datetime.utcnow().isoformat(),
        "service_name": "comment-service"
    }

    response = client.post(
        "/incidents/analyze-request",
        json=payload,
        headers={"X-API-Key": API_KEY}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["threat_score"] >= 0.60
    assert data["threat_type"] == "xss"
    assert data["should_block"] == True
    assert len(data["findings"]) > 0

def test_analyze_request_command_injection():
    """Test analyzing a command injection attack."""
    payload = {
        "request_method": "POST",
        "request_url": "http://example.com/api/system/exec",
        "request_path": "/api/system/exec",
        "request_headers": {
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0",
            "X-Forwarded-For": "192.168.1.102"
        },
        "request_body": {
            "command": "; cat /etc/passwd",
            "args": "| ls -la"
        },
        "client_ip": "192.168.1.102",
        "timestamp": datetime.utcnow().isoformat(),
        "service_name": "system-service"
    }

    response = client.post(
        "/incidents/analyze-request",
        json=payload,
        headers={"X-API-Key": API_KEY}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["threat_score"] >= 0.80
    assert data["threat_type"] == "command_injection"
    assert data["should_block"] == True
    assert len(data["findings"]) > 0

def test_analyze_request_path_traversal():
    """Test analyzing a path traversal attack."""
    payload = {
        "request_method": "GET",
        "request_url": "http://example.com/api/files/../../etc/passwd",
        "request_path": "/api/files/../../etc/passwd",
        "request_headers": {
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0",
            "X-Forwarded-For": "192.168.1.103"
        },
        "request_body": None,
        "client_ip": "192.168.1.103",
        "timestamp": datetime.utcnow().isoformat(),
        "service_name": "file-service"
    }

    response = client.post(
        "/incidents/analyze-request",
        json=payload,
        headers={"X-API-Key": API_KEY}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["threat_score"] >= 0.70
    assert data["threat_type"] == "path_traversal"
    assert data["should_block"] == True
    assert len(data["findings"]) > 0

def test_analyze_request_nosql_injection():
    """Test analyzing a NoSQL injection attack."""
    payload = {
        "request_method": "POST",
        "request_url": "http://example.com/api/users/find",
        "request_path": "/api/users/find",
        "request_headers": {
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0",
            "X-Forwarded-For": "192.168.1.104"
        },
        "request_body": {
            "username": {"$ne": None},
            "password": {"$gt": ""}
        },
        "client_ip": "192.168.1.104",
        "timestamp": datetime.utcnow().isoformat(),
        "service_name": "user-service"
    }

    response = client.post(
        "/incidents/analyze-request",
        json=payload,
        headers={"X-API-Key": API_KEY}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["threat_score"] >= 0.65
    assert data["threat_type"] == "nosql_injection"
    assert data["should_block"] == True
    assert len(data["findings"]) > 0

def test_analyze_request_safe():
    """Test analyzing a safe request."""
    payload = {
        "request_method": "GET",
        "request_url": "http://example.com/api/products",
        "request_path": "/api/products",
        "request_headers": {
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0",
            "X-Forwarded-For": "192.168.1.105"
        },
        "request_body": None,
        "client_ip": "192.168.1.105",
        "timestamp": datetime.utcnow().isoformat(),
        "service_name": "product-service"
    }

    response = client.post(
        "/incidents/analyze-request",
        json=payload,
        headers={"X-API-Key": API_KEY}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["threat_score"] < 0.50
    assert data["should_block"] == False

def test_analyze_request_missing_api_key():
    """Test request without API key."""
    payload = {
        "request_method": "GET",
        "request_url": "http://example.com/api/users",
        "request_path": "/api/users",
        "request_headers": {},
        "request_body": None,
        "client_ip": "192.168.1.106",
        "timestamp": datetime.utcnow().isoformat(),
        "service_name": "user-service"
    }

    response = client.post("/incidents/analyze-request", json=payload)
    assert response.status_code == 401
    assert "API key is required" in response.json()["detail"]

def test_analyze_request_invalid_api_key():
    """Test request with invalid API key."""
    payload = {
        "request_method": "GET",
        "request_url": "http://example.com/api/users",
        "request_path": "/api/users",
        "request_headers": {},
        "request_body": None,
        "client_ip": "192.168.1.106",
        "timestamp": datetime.utcnow().isoformat(),
        "service_name": "user-service"
    }

    response = client.post(
        "/incidents/analyze-request",
        json=payload,
        headers={"X-API-Key": "invalid_key"}
    )
    assert response.status_code == 401
    assert "Invalid API key" in response.json()["detail"] 