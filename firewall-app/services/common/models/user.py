"""User-related database models.

This module defines all models related to user management.
"""

from datetime import datetime
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, JSON, Integer, Text
from sqlalchemy.orm import relationship

from services.common.models.base import Base

class User(Base):
    """Model for storing user information."""
    
    __tablename__ = 'user'

    id = Column(String(36), primary_key=True)  # UUID
    email = Column(String(255), unique=True, nullable=False)
    name = Column(String(100), nullable=False)  # Added name field
    password_hash = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)

    # Relationships with cascade delete
    profile = relationship('UserProfile', back_populates='user', uselist=False, cascade='all, delete-orphan')
    api_keys = relationship('APIKey', back_populates='user', cascade='all, delete-orphan')
    reported_incidents = relationship('Incident', foreign_keys='Incident.reporter_id', back_populates='reporter', cascade='all, delete-orphan')
    assigned_incidents = relationship('Incident', foreign_keys='Incident.assigned_to', back_populates='assignee', cascade='all, delete-orphan')
    incident_responses = relationship('IncidentResponse', back_populates='responder', cascade='all, delete-orphan')
    notification_preferences = relationship('NotificationPreference', back_populates='user', cascade='all, delete-orphan')
    notifications = relationship('Notification', back_populates='user', cascade='all, delete-orphan')

class UserProfile(Base):
    """Model for storing additional user profile information."""
    
    __tablename__ = 'user_profile'

    id = Column(String(36), primary_key=True)  # UUID
    user_id = Column(String(36), ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    first_name = Column(String(50), nullable=True)
    last_name = Column(String(50), nullable=True)
    phone = Column(String(20), nullable=True)
    department = Column(String(100), nullable=True)
    role = Column(String(100), nullable=True)
    avatar_url = Column(String(255), nullable=True)
    bio = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship('User', back_populates='profile')

class APIKey(Base):
    """Model for storing API keys."""
    
    __tablename__ = 'api_key'

    id = Column(String(36), primary_key=True)  # UUID
    user_id = Column(String(36), ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    key = Column(String(255), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)  # Description/purpose of the key
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=True)  # Optional expiration date
    last_used_at = Column(DateTime, nullable=True)
    revoked_at = Column(DateTime, nullable=True)
    permissions = Column(Text, nullable=True)  # JSON string of permissions

    # Relationships
    user = relationship('User', back_populates='api_keys')
    malicious_requests = relationship('MaliciousRequest', back_populates='api_key', cascade='all, delete-orphan') 