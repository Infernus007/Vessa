"""Notification API schemas.

This module defines request and response models for the notification API.
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field, HttpUrl

from services.common.models.notification import NotificationChannel, NotificationPriority

class NotificationPreferenceBase(BaseModel):
    """Base model for notification preferences."""
    channel: NotificationChannel
    enabled: bool = True
    min_priority: NotificationPriority = NotificationPriority.LOW
    webhook_url: Optional[HttpUrl] = None
    email_address: Optional[str] = Field(None, max_length=255)

class NotificationPreferenceCreate(NotificationPreferenceBase):
    """Model for creating notification preferences."""
    pass

class NotificationPreferenceUpdate(BaseModel):
    """Model for updating notification preferences."""
    enabled: Optional[bool] = None
    min_priority: Optional[NotificationPriority] = None
    webhook_url: Optional[HttpUrl] = None
    email_address: Optional[str] = Field(None, max_length=255)

class NotificationPreferenceResponse(NotificationPreferenceBase):
    """Model for notification preference responses."""
    id: str
    user_id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class NotificationBase(BaseModel):
    """Base model for notifications."""
    title: str = Field(..., max_length=255)
    message: str = Field(..., max_length=2048)
    priority: NotificationPriority
    data: Optional[Dict[str, Any]] = None

class NotificationCreate(NotificationBase):
    """Model for creating notifications."""
    incident_id: Optional[str] = None

class NotificationResponse(NotificationBase):
    """Model for notification responses."""
    id: str
    user_id: str
    incident_id: Optional[str] = None
    created_at: datetime
    read_at: Optional[datetime] = None
    delivered_channels: List[NotificationChannel]

    class Config:
        from_attributes = True

class NotificationList(BaseModel):
    """Model for paginated notification list."""
    items: List[NotificationResponse]
    total: int
    unread_count: int

    class Config:
        from_attributes = True 