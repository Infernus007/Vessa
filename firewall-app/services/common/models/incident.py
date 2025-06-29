"""Incident-related database models.

This module defines all models related to incident management.
"""

from datetime import datetime
from enum import Enum
from typing import List
from sqlalchemy import Column, String, DateTime, Boolean, Integer, JSON, ForeignKey, Enum as SQLEnum, Float
from sqlalchemy.orm import relationship

from .base import Base

class SeverityLevel(str, Enum):
    """Severity levels for incidents."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class IncidentStatus(str, Enum):
    """Status values for incidents."""
    OPEN = "open"
    INVESTIGATING = "investigating"
    CONTAINED = "contained"
    RESOLVED = "resolved"
    CLOSED = "closed"

class Incident(Base):
    """Model for storing security incidents."""
    
    __tablename__ = 'incident'

    id = Column(String(36), primary_key=True)  # UUID
    title = Column(String(255), nullable=False)
    description = Column(String(2048), nullable=False)
    severity = Column(String(20), nullable=False)  # high, medium, low
    status = Column(String(20), default='open')  # open, investigating, resolved, closed
    detection_source = Column(String(50), nullable=False)  # api_gateway, waf, ids, manual
    affected_assets = Column(JSON, nullable=True)  # List of affected systems/endpoints
    tags = Column(JSON, nullable=True)  # List of tags for categorization
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    resolved_at = Column(DateTime, nullable=True)
    resolution_notes = Column(String(2048), nullable=True)
    threat_details = Column(JSON, nullable=True)  # Additional threat information
    mitigation_steps = Column(JSON, nullable=True)  # Steps taken to mitigate
    false_positive = Column(Boolean, default=False)
    reporter_id = Column(String(36), ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    assigned_to = Column(String(36), ForeignKey('user.id', ondelete='SET NULL'), nullable=True)
    closed_at = Column(DateTime, nullable=True)
    priority_score = Column(Integer, nullable=True)

    # Relationships
    reporter = relationship('User', foreign_keys=[reporter_id], back_populates='reported_incidents')
    assignee = relationship('User', foreign_keys=[assigned_to], back_populates='assigned_incidents')
    responses = relationship('IncidentResponse', back_populates='incident', cascade='all, delete-orphan')
    malicious_requests = relationship('MaliciousRequest', back_populates='incident', cascade='all, delete-orphan')
    attachments = relationship('IncidentAttachment', back_populates='incident', cascade='all, delete-orphan')
    notifications = relationship('Notification', back_populates='incident', cascade='all, delete-orphan')

class IncidentResponse(Base):
    """Model for storing incident response details."""
    
    __tablename__ = 'incidentresponse'

    id = Column(String(36), primary_key=True)  # UUID
    incident_id = Column(String(36), ForeignKey('incident.id', ondelete='CASCADE'), nullable=False)
    responder_id = Column(String(36), ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    status = Column(String(50), nullable=False, default='open')
    response_priority = Column(String(50), nullable=False, default='medium')
    assigned_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    resolved_at = Column(DateTime, nullable=True)
    resolution_summary = Column(String(2048), nullable=True)  # Fixed length for MySQL
    time_to_respond = Column(Integer, nullable=True)  # Minutes
    time_to_resolve = Column(Integer, nullable=True)  # Minutes

    # Relationships
    incident = relationship('Incident', back_populates='responses')
    responder = relationship('User', back_populates='incident_responses')
    actions = relationship('ResponseAction', back_populates='incident_response', cascade='all, delete-orphan')

class ResponseAction(Base):
    """Model for storing actions taken during incident response."""
    
    __tablename__ = 'responseaction'

    id = Column(String(36), primary_key=True)  # UUID
    response_id = Column(String(36), ForeignKey('incidentresponse.id', ondelete='CASCADE'), nullable=False)
    action_type = Column(String(50), nullable=False)
    description = Column(String(2048), nullable=False)  # Fixed length for MySQL
    performed_by = Column(String(36), ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    performed_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    result = Column(String(2048), nullable=True)  # Fixed length for MySQL
    artifacts = Column(JSON, nullable=True)

    # Relationships
    incident_response = relationship('IncidentResponse', back_populates='actions')
    user = relationship('User')

class MaliciousRequest(Base):
    """Model for storing potentially malicious requests."""
    
    __tablename__ = 'malicious_request'

    id = Column(String(36), primary_key=True)  # UUID
    source_ip = Column(String(45), nullable=False)  # IPv4/IPv6 address
    request_path = Column(String(2048), nullable=False)
    request_method = Column(String(10), nullable=False)
    threat_type = Column(String(50), nullable=False)
    threat_score = Column(Float, nullable=False)
    headers = Column(JSON, nullable=True)
    body = Column(JSON, nullable=True)
    user_agent = Column(String(512), nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    is_blocked = Column(Boolean, default=False)
    incident_id = Column(String(36), ForeignKey('incident.id', ondelete='CASCADE'), nullable=True)
    api_key_id = Column(String(36), ForeignKey('api_key.id', ondelete='CASCADE'), nullable=True)  # Link to API key
    threat_details = Column(JSON, nullable=True)  # Detailed threat analysis information

    # Relationships
    incident = relationship('Incident', back_populates='malicious_requests')
    api_key = relationship('APIKey', back_populates='malicious_requests')

class IncidentAttachment(Base):
    """Model for storing incident attachments."""
    
    __tablename__ = 'incidentattachment'

    id = Column(String(36), primary_key=True)  # UUID
    incident_id = Column(String(36), ForeignKey('incident.id', ondelete='CASCADE'), nullable=False)
    filename = Column(String(255), nullable=False)
    content_type = Column(String(100), nullable=False)
    file_size = Column(Integer, nullable=False)
    storage_path = Column(String(512), nullable=False)
    uploader_id = Column(String(36), ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    description = Column(String(1024), nullable=True)  # Fixed length for MySQL

    # Relationships
    incident = relationship('Incident', back_populates='attachments')
    uploader = relationship('User') 