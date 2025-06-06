"""Notification models.

This module defines models for storing notifications and notification preferences.
"""

from datetime import datetime
from enum import Enum
from sqlalchemy import Column, String, DateTime, Boolean, ForeignKey, JSON, Enum as SQLEnum
from sqlalchemy.orm import relationship

from .base import Base

class NotificationChannel(str, Enum):
    """Available notification channels."""
    EMAIL = "email"
    WEBSOCKET = "websocket"
    WEBHOOK = "webhook"

class NotificationPriority(str, Enum):
    """Notification priority levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class NotificationPreference(Base):
    """Model for storing user notification preferences."""
    
    __tablename__ = 'notification_preference'

    id = Column(String(36), primary_key=True)  # UUID
    user_id = Column(String(36), ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    channel = Column(SQLEnum(NotificationChannel), nullable=False)
    enabled = Column(Boolean, default=True)
    min_priority = Column(SQLEnum(NotificationPriority), default=NotificationPriority.LOW)
    webhook_url = Column(String(512), nullable=True)  # For webhook notifications
    email_address = Column(String(255), nullable=True)  # For custom email address
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship('User', back_populates='notification_preferences')

class Notification(Base):
    """Model for storing notifications."""
    
    __tablename__ = 'notification'

    id = Column(String(36), primary_key=True)  # UUID
    user_id = Column(String(36), ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    title = Column(String(255), nullable=False)
    message = Column(String(2048), nullable=False)
    priority = Column(SQLEnum(NotificationPriority), nullable=False)
    data = Column(JSON, nullable=True)  # Additional notification data
    incident_id = Column(String(36), ForeignKey('incident.id', ondelete='CASCADE'), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    read_at = Column(DateTime, nullable=True)
    delivered_channels = Column(JSON, default=list)  # List of channels notification was sent through

    # Relationships
    user = relationship('User', back_populates='notifications')
    incident = relationship('Incident', back_populates='notifications') 