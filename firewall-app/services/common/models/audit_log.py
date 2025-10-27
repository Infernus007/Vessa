"""Audit Log Model.

This module defines the audit log model for tracking security-relevant events.
"""

from datetime import datetime
from sqlalchemy import Column, String, Text, DateTime, JSON, Index
from services.common.models.base import Base


class AuditLog(Base):
    """Audit log for security-relevant events.
    
    Records all important security events for compliance and forensics.
    """
    
    __tablename__ = 'audit_log'
    
    # Primary fields
    id = Column(String(36), primary_key=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    # Event details
    event_type = Column(String(50), nullable=False, index=True)  # login, logout, create, update, delete, etc.
    event_category = Column(String(50), nullable=False, index=True)  # auth, incident, user, api_key, etc.
    action = Column(String(100), nullable=False)  # user_login, incident_created, api_key_revoked, etc.
    
    # Actor information
    user_id = Column(String(36), nullable=True, index=True)  # Who performed the action
    user_email = Column(String(255), nullable=True)
    ip_address = Column(String(45), nullable=True, index=True)  # IPv4 or IPv6
    user_agent = Column(String(512), nullable=True)
    
    # Resource information
    resource_type = Column(String(50), nullable=True)  # user, incident, api_key, etc.
    resource_id = Column(String(36), nullable=True, index=True)  # ID of affected resource
    
    # Details
    description = Column(Text, nullable=False)
    event_metadata = Column(JSON, nullable=True)  # Additional structured data (renamed from metadata to avoid SQLAlchemy conflict)
    
    # Result
    status = Column(String(20), nullable=False, default='success')  # success, failure, error
    error_message = Column(Text, nullable=True)  # If status is failure/error
    
    # Request context
    request_id = Column(String(36), nullable=True)  # For correlating with requests
    api_endpoint = Column(String(255), nullable=True)  # API endpoint called
    http_method = Column(String(10), nullable=True)  # GET, POST, etc.
    
    # Compliance and retention
    retention_days = Column(String(10), default='2555')  # 7 years default (compliance)
    
    # Indexes for common queries
    __table_args__ = (
        Index('idx_audit_timestamp_event', 'timestamp', 'event_type'),
        Index('idx_audit_user_timestamp', 'user_id', 'timestamp'),
        Index('idx_audit_resource', 'resource_type', 'resource_id'),
        Index('idx_audit_category_action', 'event_category', 'action'),
    )
    
    def __repr__(self):
        return f"<AuditLog {self.id}: {self.action} by {self.user_email} at {self.timestamp}>"

