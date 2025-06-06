"""Tests for authentication API routes.

This module contains test cases for the authentication endpoints.
"""

import os
import sys
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Add the project directory to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../..')))

from main import app
from services.common.models.base import Base
from services.common.models.user import User
from services.common.database.session import get_db
from services.common.utils.security import get_password_hash

# Test database configuration
os.environ["DB_NAME"] = "vessa_test"
os.environ["DB_USER"] = "root"
os.environ["DB_PASSWORD"] = "root"
os.environ["DB_HOST"] = "localhost"
os.environ["DB_PORT"] = "3306"

from services.common.database.session import get_database_url

# Create test database if it doesn't exist
def create_test_database():
    """Create test database if it doesn't exist."""
    # Create a new engine without specifying the database
    tmp_engine = create_engine(
        f"mysql+mysqlconnector://{os.environ['DB_USER']}:{os.environ['DB_PASSWORD']}@{os.environ['DB_HOST']}:{os.environ['DB_PORT']}"
    )
    
    with tmp_engine.connect() as conn:
        conn.execute(text(f"CREATE DATABASE IF NOT EXISTS {os.environ['DB_NAME']}"))
        conn.commit()

# Create test database before running tests
create_test_database()

# Create test engine
engine = create_engine(
    get_database_url(),
    pool_pre_ping=True,
    pool_recycle=300
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="function")
def db_session():
    """Create a fresh database session for each test."""
    # Drop and recreate all tables for each test
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

@pytest.fixture
def client(db_session):
    """Create a test client with a test database session."""
    def override_get_db():
        try:
            yield db_session
        finally:
            db_session.close()
    
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()

@pytest.fixture
def test_company(db_session):
    """Create a test company account."""
    user = User(
        id="12345678-1234-5678-1234-567812345678",  # Fixed UUID for testing
        email="test@example.com",
        name="Test Company Inc.",
        hashed_password=get_password_hash("testpassword123"),
        role="client",
        is_active=True,
        company_domain="example.com",
        allowed_domains=["example.com", "test.example.com"],
        subscription_tier="basic"
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user

import requests

def test_me_endpoint():
    token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJuYW1lQGdtYWlsLmNvbSIsImV4cCI6MTc0MjUwNTQwMiwidHlwZSI6ImFjY2VzcyJ9.Y4EJNIel1LzLrKJjj6hG2wohhMxxCOsF89QROKNOSFk"
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json"
    }
    
    response = requests.get(
        "http://localhost:8000/users/me",
        headers=headers
    )
    
    print(f"Status Code: {response.status_code}")
    print(f"Headers: {response.headers}")
    try:
        print(f"Response: {response.json()}")
    except:
        print(f"Raw Response: {response.text}")

test_me_endpoint()

def test_register_company(client):
    """Test company registration endpoint."""
    response = client.post(
        "/auth/register",
        json={
            "email": "newcompany@example.com",
            "password": "Password123!",
            "name": "New Company LLC",
            "role": "client",
            "company_domain": "newcompany.com",
            "allowed_domains": ["newcompany.com", "api.newcompany.com"]
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "newcompany@example.com"
    assert data["name"] == "New Company LLC"
    assert data["company_domain"] == "newcompany.com"
    assert "id" in data
    assert "password" not in data

def test_register_duplicate_email(client, test_company):
    """Test registration with existing email."""
    response = client.post(
        "/auth/register",
        json={
            "email": "test@example.com",
            "password": "Password123!",
            "name": "Another Company",
            "role": "client",
            "company_domain": "another.com"
        }
    )
    assert response.status_code == 400
    assert "email already registered" in response.json()["detail"].lower()

def test_login_success(client, test_company):
    """Test successful login."""
    response = client.post(
        "/auth/token",
        data={
            "username": "test@example.com",
            "password": "testpassword123"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_login_invalid_credentials(client):
    """Test login with invalid credentials."""
    response = client.post(
        "/auth/token",
        data={
            "username": "wrong@example.com",
            "password": "wrongpassword"
        }
    )
    assert response.status_code == 401
    assert "incorrect email or password" in response.json()["detail"].lower()

def test_change_password(client, test_company):
    """Test password change endpoint."""
    # First login to get token
    login_response = client.post(
        "/auth/token",
        data={
            "username": "test@example.com",
            "password": "testpassword123"
        }
    )
    token = login_response.json()["access_token"]
    
    # Change password
    response = client.post(
        "/auth/change-password",
        json={
            "current_password": "testpassword123",
            "new_password": "NewPassword123!"
        },
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert response.json()["message"] == "Password changed successfully"
    
    # Try logging in with new password
    login_response = client.post(
        "/auth/token",
        data={
            "username": "test@example.com",
            "password": "NewPassword123!"
        }
    )
    assert login_response.status_code == 200

def test_change_password_wrong_current(client, test_company):
    """Test password change with wrong current password."""
    # First login to get token
    login_response = client.post(
        "/auth/token",
        data={
            "username": "test@example.com",
            "password": "testpassword123"
        }
    )
    token = login_response.json()["access_token"]
    
    # Try changing password with wrong current password
    response = client.post(
        "/auth/change-password",
        json={
            "current_password": "wrongpassword",
            "new_password": "NewPassword123!"
        },
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 400
    assert "current password is incorrect" in response.json()["detail"].lower()

def test_get_current_user(client, test_company):
    """Test getting current user information."""
    # First login to get token
    login_response = client.post(
        "/auth/token",
        data={
            "username": "test@example.com",
            "password": "testpassword123"
        }
    )
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]
    
    # Test /users/me endpoint
    response = client.get(
        "/users/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
    
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "test@example.com"
    assert data["name"] == "Test Company Inc."
    assert data["role"] == "client"
    assert data["company_domain"] == "example.com"
    assert data["allowed_domains"] == ["example.com", "test.example.com"]

def test_get_current_user_no_token(client):
    """Test getting current user without authentication."""
    response = client.get("/users/me")
    assert response.status_code == 401
    assert "not authenticated" in response.json()["detail"].lower()

if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 