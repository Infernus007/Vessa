"""Test incident API routes."""

import pytest
from fastapi.testclient import TestClient
from datetime import datetime, timedelta
import uuid

from main import app
from services.common.models.incident import Incident
from services.common.models.user import User

client = TestClient(app)

@pytest.fixture
def test_user(db_session):
    """Create a test user."""
    user = User(
        id=str(uuid.uuid4()),
        email="test@example.com",
        name="Test User",
        hashed_password="dummy_hash"
    )
    db_session.add(user)
    db_session.commit()
    return user

@pytest.fixture
def test_incidents(db_session, test_user):
    """Create test incidents."""
    incidents = []
    for i in range(5):
        incident = Incident(
            id=str(uuid.uuid4()),
            title=f"Test Incident {i}",
            description=f"Description for test incident {i}",
            severity="high" if i % 2 == 0 else "medium",
            status="open",
            reporter_id=test_user.id,
            created_at=datetime.utcnow() - timedelta(hours=i)
        )
        incidents.append(incident)
        db_session.add(incident)
    
    db_session.commit()
    return incidents

def test_list_incidents(db_session, test_incidents):
    """Test listing incidents."""
    response = client.get("/incidents/")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert len(data["items"]) == len(test_incidents)

def test_get_incident(db_session, test_incidents):
    """Test getting a specific incident."""
    incident = test_incidents[0]
    response = client.get(f"/incidents/{incident.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == incident.id
    assert data["title"] == incident.title

def test_create_incident(db_session, test_user):
    """Test creating an incident."""
    incident_data = {
        "title": "New Test Incident",
        "description": "Test description",
        "severity": "high",
        "affected_assets": ["server-01"],
        "tags": ["test"]
    }
    response = client.post("/incidents/", json=incident_data)
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == incident_data["title"]
    assert data["severity"] == incident_data["severity"]

def test_update_incident(db_session, test_incidents):
    """Test updating an incident."""
    incident = test_incidents[0]
    update_data = {
        "title": "Updated Title",
        "status": "resolved",
        "resolution_notes": "Issue resolved"
    }
    response = client.put(f"/incidents/{incident.id}", json=update_data)
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == update_data["title"]
    assert data["status"] == update_data["status"]

def test_get_recent_incidents(db_session, test_incidents, test_user):
    """Test getting recent incidents."""
    response = client.get("/incidents/recent?limit=3&offset=0")
    assert response.status_code == 200
    data = response.json()
    assert "incidents" in data
    assert len(data["incidents"]) == 3
    assert data["total_count"] == len(test_incidents)
    assert "has_more" in data
    
    # Verify incident format
    incident = data["incidents"][0]
    assert "id" in incident
    assert "title" in incident
    assert "status" in incident
    assert "severity" in incident
    assert "timestamp" in incident
    assert "reporter" in incident
    assert "is_system_report" in incident
    
    # Verify reporter info
    reporter = incident["reporter"]
    assert reporter["name"] == test_user.name
    assert reporter["email"] == test_user.email
    assert "avatar" in reporter

def test_get_recent_incidents_pagination(db_session, test_incidents):
    """Test recent incidents pagination."""
    # First page
    response = client.get("/incidents/recent?limit=2&offset=0")
    assert response.status_code == 200
    data = response.json()
    assert len(data["incidents"]) == 2
    assert data["has_more"] == True
    first_page_ids = [i["id"] for i in data["incidents"]]
    
    # Second page
    response = client.get("/incidents/recent?limit=2&offset=2")
    assert response.status_code == 200
    data = response.json()
    assert len(data["incidents"]) == 2
    second_page_ids = [i["id"] for i in data["incidents"]]
    
    # Verify different incidents
    assert not set(first_page_ids).intersection(set(second_page_ids))

def test_get_recent_incidents_empty(db_session):
    """Test getting recent incidents with empty database."""
    response = client.get("/incidents/recent?limit=5&offset=0")
    assert response.status_code == 200
    data = response.json()
    assert len(data["incidents"]) == 0
    assert data["total_count"] == 0
    assert data["has_more"] == False

def test_get_analytics_overview(db_session, test_incidents):
    """Test getting analytics overview."""
    response = client.get("/incidents/analytics/overview?time_range=24h")
    assert response.status_code == 200
    data = response.json()
    assert "total_requests" in data
    assert "blocked_requests" in data
    assert "block_rate" in data
    assert "avg_threat_score" in data
    assert "threat_distribution" in data
    assert data["time_range"] == "24h"

def test_get_time_series_analytics(db_session, test_incidents):
    """Test getting time series analytics."""
    response = client.get("/incidents/analytics/time-series?metric=threats&interval=1h&time_range=24h")
    assert response.status_code == 200
    data = response.json()
    assert "metric" in data
    assert "interval" in data
    assert "time_range" in data
    assert "data" in data
    assert isinstance(data["data"], list)

def test_get_user_engagement_metrics(db_session, test_user, test_incidents):
    """Test getting user engagement metrics."""
    response = client.get("/incidents/analytics/engagement?time_range=30d")
    assert response.status_code == 200
    data = response.json()
    assert "user_engagement" in data
    assert "time_range" in data
    assert isinstance(data["user_engagement"], dict)
    
    # Verify user metrics
    user_metrics = data["user_engagement"].get(test_user.id, {})
    if user_metrics:
        assert "name" in user_metrics
        assert "email" in user_metrics
        assert "metrics" in user_metrics
        metrics = user_metrics["metrics"]
        assert "reported_incidents" in metrics
        assert "assigned_incidents" in metrics
        assert "incident_responses" in metrics
        assert "total_engagement" in metrics

def test_get_team_analytics(db_session, test_user, test_incidents):
    """Test getting team analytics."""
    response = client.get("/incidents/analytics/team?time_range=30d")
    assert response.status_code == 200
    data = response.json()
    assert "team_members" in data
    assert "total_responses" in data
    assert "member_metrics" in data
    assert "workload_distribution" in data
    assert "time_range" in data
    
    # Verify member metrics
    member_metrics = data["member_metrics"].get(test_user.id, {})
    if member_metrics:
        assert "name" in member_metrics
        assert "email" in member_metrics
        assert "metrics" in member_metrics
        metrics = member_metrics["metrics"]
        assert "total_responses" in metrics
        assert "avg_response_time" in metrics
        assert "avg_resolution_time" in metrics

def test_get_user_performance_metrics(db_session, test_user, test_incidents):
    """Test getting user performance metrics."""
    response = client.get("/incidents/analytics/user-performance?time_range=30d&top_n=5")
    assert response.status_code == 200
    data = response.json()
    assert "top_performers" in data
    assert "time_range" in data
    assert isinstance(data["top_performers"], list)
    
    if data["top_performers"]:
        performer = data["top_performers"][0]
        assert "user_id" in performer
        assert "name" in performer
        assert "email" in performer
        assert "metrics" in performer 