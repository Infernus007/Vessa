"""Notification service.

This module provides functionality for sending notifications through various channels.
"""

import uuid
from datetime import datetime
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from fastapi import WebSocket
import aiosmtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import httpx
import json
import logging

from services.common.models.notification import (
    Notification,
    NotificationPreference,
    NotificationChannel,
    NotificationPriority
)
from services.common.models.user import User
from services.common.config import Settings

logger = logging.getLogger(__name__)

class NotificationService:
    """Service for managing and sending notifications."""

    def __init__(self, db: Session):
        """Initialize the service.
        
        Args:
            db: Database session
        """
        self.db = db
        self.settings = Settings()
        self.active_websockets: Dict[str, WebSocket] = {}  # user_id -> websocket

    async def create_notification(
        self,
        user_id: str,
        title: str,
        message: str,
        priority: NotificationPriority,
        incident_id: Optional[str] = None,
        data: Optional[Dict] = None
    ) -> Notification:
        """Create and send a new notification.
        
        Args:
            user_id: User ID to notify
            title: Notification title
            message: Notification message
            priority: Notification priority
            incident_id: Related incident ID (optional)
            data: Additional notification data (optional)
            
        Returns:
            Created notification
        """
        # Create notification record
        notification = Notification(
            id=str(uuid.uuid4()),
            user_id=user_id,
            title=title,
            message=message,
            priority=priority,
            incident_id=incident_id,
            data=data or {},
            delivered_channels=[]
        )
        self.db.add(notification)
        
        # Get user's notification preferences
        preferences = self.db.query(NotificationPreference).filter(
            NotificationPreference.user_id == user_id,
            NotificationPreference.enabled == True,
            NotificationPreference.min_priority <= priority
        ).all()
        
        # Send through each enabled channel
        for pref in preferences:
            if pref.channel == NotificationChannel.EMAIL and pref.email_address:
                await self._send_email_notification(notification, pref.email_address)
                notification.delivered_channels.append(NotificationChannel.EMAIL)
                
            elif pref.channel == NotificationChannel.WEBSOCKET:
                await self._send_websocket_notification(notification)
                notification.delivered_channels.append(NotificationChannel.WEBSOCKET)
                
            elif pref.channel == NotificationChannel.WEBHOOK and pref.webhook_url:
                await self._send_webhook_notification(notification, pref.webhook_url)
                notification.delivered_channels.append(NotificationChannel.WEBHOOK)
        
        self.db.commit()
        return notification

    async def _send_email_notification(
        self,
        notification: Notification,
        email_address: str
    ) -> None:
        """Send notification via email.
        
        Args:
            notification: Notification to send
            email_address: Recipient email address
        """
        message = MIMEMultipart()
        message["From"] = self.settings.smtp_from_address
        message["To"] = email_address
        message["Subject"] = f"[{notification.priority.upper()}] {notification.title}"
        
        # Create HTML body
        html = f"""
        <html>
            <body>
                <h2>{notification.title}</h2>
                <p>{notification.message}</p>
                <hr>
                <p><small>Priority: {notification.priority}</small></p>
                <p><small>Time: {notification.created_at}</small></p>
            </body>
        </html>
        """
        message.attach(MIMEText(html, "html"))
        
        # Send email
        await aiosmtplib.send(
            message,
            hostname=self.settings.smtp_host,
            port=self.settings.smtp_port,
            username=self.settings.smtp_username,
            password=self.settings.smtp_password,
            use_tls=True
        )

    async def _send_websocket_notification(self, notification: Notification) -> None:
        """Send notification via WebSocket if user is connected.
        
        Args:
            notification: Notification to send
        """
        logger.debug("Attempting to send WebSocket notification", extra={"user_id": notification.user_id})
        logger.debug("Active WebSocket connections", extra={"connections": list(self.active_websockets.keys())})
        
        if notification.user_id in self.active_websockets:
            websocket = self.active_websockets[notification.user_id]
            try:
                logger.debug("Found active WebSocket for user", extra={"user_id": notification.user_id})
                message = {
                    "type": "notification",
                    "data": {
                        "id": notification.id,
                        "title": notification.title,
                        "message": notification.message,
                        "priority": notification.priority,
                        "created_at": notification.created_at.isoformat(),
                        "data": notification.data
                    }
                }
                logger.debug("Sending WebSocket message", extra={"message_type": message.get("type")})
                await websocket.send_json(message)
                logger.debug("Successfully sent WebSocket notification", extra={"user_id": notification.user_id})
            except Exception as e:
                logger.error("Failed to send WebSocket notification", extra={"user_id": notification.user_id, "error": str(e)})
                # Remove dead connection
                del self.active_websockets[notification.user_id]
        else:
            logger.debug("No active WebSocket connection found", extra={"user_id": notification.user_id})

    async def _send_webhook_notification(
        self,
        notification: Notification,
        webhook_url: str
    ) -> None:
        """Send notification via webhook.
        
        Args:
            notification: Notification to send
            webhook_url: Webhook URL
        """
        async with httpx.AsyncClient() as client:
            await client.post(
                webhook_url,
                json={
                    "id": notification.id,
                    "title": notification.title,
                    "message": notification.message,
                    "priority": notification.priority,
                    "created_at": notification.created_at.isoformat(),
                    "data": notification.data
                },
                timeout=5.0
            )

    async def register_websocket(self, user_id: str, websocket: WebSocket) -> None:
        """Register an active WebSocket connection for a user.
        
        Args:
            user_id: User ID
            websocket: WebSocket connection
        """
        self.active_websockets[user_id] = websocket

    async def unregister_websocket(self, user_id: str) -> None:
        """Unregister a WebSocket connection.
        
        Args:
            user_id: User ID
        """
        if user_id in self.active_websockets:
            del self.active_websockets[user_id]

    def get_user_notifications(
        self,
        user_id: str,
        unread_only: bool = False,
        limit: int = 50,
        offset: int = 0
    ) -> List[Notification]:
        """Get notifications for a user.
        
        Args:
            user_id: User ID
            unread_only: Only return unread notifications
            limit: Maximum number of notifications
            offset: Number of notifications to skip
            
        Returns:
            List of notifications
        """
        query = self.db.query(Notification).filter(
            Notification.user_id == user_id
        )
        
        if unread_only:
            query = query.filter(Notification.read_at == None)
            
        return query.order_by(Notification.created_at.desc()).offset(offset).limit(limit).all()

    def mark_notification_read(self, notification_id: str, user_id: str) -> None:
        """Mark a notification as read.
        
        Args:
            notification_id: Notification ID
            user_id: User ID
        """
        notification = self.db.query(Notification).filter(
            Notification.id == notification_id,
            Notification.user_id == user_id
        ).first()
        
        if notification and not notification.read_at:
            notification.read_at = datetime.utcnow()
            self.db.commit() 