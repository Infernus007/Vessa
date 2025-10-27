"""Audit Logging Service.

This module provides comprehensive audit logging for security-relevant events.
"""

import uuid
from datetime import datetime
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from fastapi import Request

from services.common.models.audit_log import AuditLog


class AuditLogger:
    """Service for logging security-relevant events."""
    
    # Event types
    EVENT_AUTH = "authentication"
    EVENT_AUTHZ = "authorization"
    EVENT_CREATE = "create"
    EVENT_READ = "read"
    EVENT_UPDATE = "update"
    EVENT_DELETE = "delete"
    EVENT_ADMIN = "administrative"
    EVENT_SECURITY = "security"
    
    # Event categories
    CATEGORY_AUTH = "auth"
    CATEGORY_USER = "user"
    CATEGORY_INCIDENT = "incident"
    CATEGORY_API_KEY = "api_key"
    CATEGORY_NOTIFICATION = "notification"
    CATEGORY_CONFIG = "configuration"
    CATEGORY_DATA = "data"
    
    # Status
    STATUS_SUCCESS = "success"
    STATUS_FAILURE = "failure"
    STATUS_ERROR = "error"
    
    def __init__(self, db: Session):
        """Initialize the audit logger.
        
        Args:
            db: Database session
        """
        self.db = db
    
    def log(
        self,
        event_type: str,
        event_category: str,
        action: str,
        description: str,
        user_id: Optional[str] = None,
        user_email: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        status: str = STATUS_SUCCESS,
        error_message: Optional[str] = None,
        request_id: Optional[str] = None,
        api_endpoint: Optional[str] = None,
        http_method: Optional[str] = None,
        retention_days: int = 2555
    ) -> AuditLog:
        """Log an audit event.
        
        Args:
            event_type: Type of event (authentication, create, update, etc.)
            event_category: Category (auth, user, incident, etc.)
            action: Specific action (user_login, incident_created, etc.)
            description: Human-readable description
            user_id: ID of user performing action
            user_email: Email of user performing action
            ip_address: IP address of actor
            user_agent: User agent string
            resource_type: Type of resource affected
            resource_id: ID of resource affected
            metadata: Additional structured data
            status: success, failure, or error
            error_message: Error message if status is not success
            request_id: Request ID for correlation
            api_endpoint: API endpoint called
            http_method: HTTP method used
            retention_days: Days to retain this log (default 7 years for compliance)
            
        Returns:
            Created AuditLog instance
        """
        audit_log = AuditLog(
            id=str(uuid.uuid4()),
            timestamp=datetime.utcnow(),
            event_type=event_type,
            event_category=event_category,
            action=action,
            description=description,
            user_id=user_id,
            user_email=user_email,
            ip_address=ip_address,
            user_agent=user_agent,
            resource_type=resource_type,
            resource_id=resource_id,
            event_metadata=metadata,  # Fixed: renamed to event_metadata
            status=status,
            error_message=error_message,
            request_id=request_id,
            api_endpoint=api_endpoint,
            http_method=http_method,
            retention_days=str(retention_days)
        )
        
        self.db.add(audit_log)
        self.db.commit()
        
        return audit_log
    
    def log_from_request(
        self,
        request: Request,
        event_type: str,
        event_category: str,
        action: str,
        description: str,
        user_id: Optional[str] = None,
        user_email: Optional[str] = None,
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        status: str = STATUS_SUCCESS,
        error_message: Optional[str] = None
    ) -> AuditLog:
        """Log an audit event with details extracted from FastAPI Request.
        
        Args:
            request: FastAPI Request object
            ... (other parameters same as log())
            
        Returns:
            Created AuditLog instance
        """
        # Extract request details
        ip_address = request.client.host if request.client else None
        user_agent = request.headers.get("user-agent", None)
        api_endpoint = str(request.url.path)
        http_method = request.method
        request_id = request.headers.get("x-request-id", str(uuid.uuid4()))
        
        return self.log(
            event_type=event_type,
            event_category=event_category,
            action=action,
            description=description,
            user_id=user_id,
            user_email=user_email,
            ip_address=ip_address,
            user_agent=user_agent,
            resource_type=resource_type,
            resource_id=resource_id,
            metadata=metadata,
            status=status,
            error_message=error_message,
            request_id=request_id,
            api_endpoint=api_endpoint,
            http_method=http_method
        )
    
    # Convenience methods for common events
    
    def log_login_success(self, user_id: str, user_email: str, ip_address: str, user_agent: str):
        """Log successful login."""
        return self.log(
            event_type=self.EVENT_AUTH,
            event_category=self.CATEGORY_AUTH,
            action="user_login",
            description=f"User {user_email} logged in successfully",
            user_id=user_id,
            user_email=user_email,
            ip_address=ip_address,
            user_agent=user_agent,
            status=self.STATUS_SUCCESS
        )
    
    def log_login_failure(self, email: str, ip_address: str, reason: str):
        """Log failed login attempt."""
        return self.log(
            event_type=self.EVENT_AUTH,
            event_category=self.CATEGORY_AUTH,
            action="user_login_failed",
            description=f"Failed login attempt for {email}: {reason}",
            user_email=email,
            ip_address=ip_address,
            status=self.STATUS_FAILURE,
            error_message=reason
        )
    
    def log_logout(self, user_id: str, user_email: str):
        """Log user logout."""
        return self.log(
            event_type=self.EVENT_AUTH,
            event_category=self.CATEGORY_AUTH,
            action="user_logout",
            description=f"User {user_email} logged out",
            user_id=user_id,
            user_email=user_email,
            status=self.STATUS_SUCCESS
        )
    
    def log_api_key_created(self, user_id: str, user_email: str, api_key_id: str, key_name: str):
        """Log API key creation."""
        return self.log(
            event_type=self.EVENT_CREATE,
            event_category=self.CATEGORY_API_KEY,
            action="api_key_created",
            description=f"User {user_email} created API key: {key_name}",
            user_id=user_id,
            user_email=user_email,
            resource_type="api_key",
            resource_id=api_key_id,
            metadata={"key_name": key_name},
            status=self.STATUS_SUCCESS
        )
    
    def log_api_key_revoked(self, user_id: str, user_email: str, api_key_id: str, key_name: str):
        """Log API key revocation."""
        return self.log(
            event_type=self.EVENT_DELETE,
            event_category=self.CATEGORY_API_KEY,
            action="api_key_revoked",
            description=f"User {user_email} revoked API key: {key_name}",
            user_id=user_id,
            user_email=user_email,
            resource_type="api_key",
            resource_id=api_key_id,
            metadata={"key_name": key_name},
            status=self.STATUS_SUCCESS
        )
    
    def log_incident_created(self, user_id: str, user_email: str, incident_id: str, title: str, severity: str):
        """Log incident creation."""
        return self.log(
            event_type=self.EVENT_CREATE,
            event_category=self.CATEGORY_INCIDENT,
            action="incident_created",
            description=f"Incident created: {title} (Severity: {severity})",
            user_id=user_id,
            user_email=user_email,
            resource_type="incident",
            resource_id=incident_id,
            metadata={"title": title, "severity": severity},
            status=self.STATUS_SUCCESS
        )
    
    def log_incident_updated(self, user_id: str, user_email: str, incident_id: str, title: str, changes: Dict):
        """Log incident update."""
        return self.log(
            event_type=self.EVENT_UPDATE,
            event_category=self.CATEGORY_INCIDENT,
            action="incident_updated",
            description=f"Incident updated: {title}",
            user_id=user_id,
            user_email=user_email,
            resource_type="incident",
            resource_id=incident_id,
            metadata={"title": title, "changes": changes},
            status=self.STATUS_SUCCESS
        )
    
    def log_unauthorized_access(self, ip_address: str, api_endpoint: str, reason: str):
        """Log unauthorized access attempt."""
        return self.log(
            event_type=self.EVENT_SECURITY,
            event_category=self.CATEGORY_AUTH,
            action="unauthorized_access",
            description=f"Unauthorized access attempt to {api_endpoint}: {reason}",
            ip_address=ip_address,
            api_endpoint=api_endpoint,
            status=self.STATUS_FAILURE,
            error_message=reason
        )
    
    def log_password_changed(self, user_id: str, user_email: str, ip_address: str):
        """Log password change."""
        return self.log(
            event_type=self.EVENT_UPDATE,
            event_category=self.CATEGORY_AUTH,
            action="password_changed",
            description=f"User {user_email} changed their password",
            user_id=user_id,
            user_email=user_email,
            ip_address=ip_address,
            resource_type="user",
            resource_id=user_id,
            status=self.STATUS_SUCCESS
        )
    
    def log_user_created(self, creator_id: str, creator_email: str, new_user_id: str, new_user_email: str):
        """Log user creation."""
        return self.log(
            event_type=self.EVENT_CREATE,
            event_category=self.CATEGORY_USER,
            action="user_created",
            description=f"{creator_email} created new user: {new_user_email}",
            user_id=creator_id,
            user_email=creator_email,
            resource_type="user",
            resource_id=new_user_id,
            metadata={"new_user_email": new_user_email},
            status=self.STATUS_SUCCESS
        )
    
    def log_config_change(self, user_id: str, user_email: str, config_key: str, old_value: Any, new_value: Any):
        """Log configuration change."""
        return self.log(
            event_type=self.EVENT_UPDATE,
            event_category=self.CATEGORY_CONFIG,
            action="config_changed",
            description=f"Configuration {config_key} changed by {user_email}",
            user_id=user_id,
            user_email=user_email,
            resource_type="configuration",
            resource_id=config_key,
            metadata={"old_value": str(old_value), "new_value": str(new_value)},
            status=self.STATUS_SUCCESS
        )


# Singleton instance for easy access
_audit_logger_instance = None

def get_audit_logger(db: Session) -> AuditLogger:
    """Get audit logger instance."""
    return AuditLogger(db)

