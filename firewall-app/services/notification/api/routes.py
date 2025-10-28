"""Notification API routes.

This module provides FastAPI routes for notification management.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect, Query
from sqlalchemy.orm import Session
import uuid
import logging

from services.common.database.session import get_db
from services.common.models.notification import NotificationChannel, NotificationPriority, NotificationPreference, Notification
from services.notification.core.notification_service import NotificationService
from services.auth.api.routes import get_current_active_user
from services.common.models.user import User
from .schemas import (
    NotificationPreferenceCreate,
    NotificationPreferenceUpdate,
    NotificationPreferenceResponse,
    NotificationResponse,
    NotificationList
)
from services.auth.core.auth_service import AuthService

router = APIRouter(tags=["notifications"])
logger = logging.getLogger(__name__)

def get_notification_service(db: Session = Depends(get_db)) -> NotificationService:
    """Get NotificationService instance."""
    return NotificationService(db)

@router.get("/preferences", response_model=List[NotificationPreferenceResponse])
async def get_notification_preferences(
    current_user: User = Depends(get_current_active_user),
    service: NotificationService = Depends(get_notification_service)
):
    """Get user's notification preferences."""
    return service.db.query(NotificationPreference).filter(
        NotificationPreference.user_id == current_user.id
    ).all()

@router.post("/preferences", response_model=NotificationPreferenceResponse)
async def create_notification_preference(
    preference: NotificationPreferenceCreate,
    current_user: User = Depends(get_current_active_user),
    service: NotificationService = Depends(get_notification_service)
):
    """Create a new notification preference."""
    # Check if preference already exists
    existing = service.db.query(NotificationPreference).filter(
        NotificationPreference.user_id == current_user.id,
        NotificationPreference.channel == preference.channel
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=400,
            detail=f"Preference for channel {preference.channel} already exists"
        )
    
    new_preference = NotificationPreference(
        id=str(uuid.uuid4()),
        user_id=current_user.id,
        **preference.dict()
    )
    service.db.add(new_preference)
    service.db.commit()
    service.db.refresh(new_preference)
    return new_preference

@router.patch("/preferences/{preference_id}", response_model=NotificationPreferenceResponse)
async def update_notification_preference(
    preference_id: str,
    update_data: NotificationPreferenceUpdate,
    current_user: User = Depends(get_current_active_user),
    service: NotificationService = Depends(get_notification_service)
):
    """Update a notification preference."""
    preference = service.db.query(NotificationPreference).filter(
        NotificationPreference.id == preference_id,
        NotificationPreference.user_id == current_user.id
    ).first()
    
    if not preference:
        raise HTTPException(status_code=404, detail="Preference not found")
    
    for key, value in update_data.dict(exclude_unset=True).items():
        setattr(preference, key, value)
    
    service.db.commit()
    service.db.refresh(preference)
    return preference

@router.delete("/preferences/{preference_id}")
async def delete_notification_preference(
    preference_id: str,
    current_user: User = Depends(get_current_active_user),
    service: NotificationService = Depends(get_notification_service)
):
    """Delete a notification preference."""
    preference = service.db.query(NotificationPreference).filter(
        NotificationPreference.id == preference_id,
        NotificationPreference.user_id == current_user.id
    ).first()
    
    if not preference:
        raise HTTPException(status_code=404, detail="Preference not found")
    
    service.db.delete(preference)
    service.db.commit()
    return {"status": "success"}

@router.get("/", response_model=NotificationList)
async def list_notifications(
    unread_only: bool = Query(False),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_active_user),
    service: NotificationService = Depends(get_notification_service)
):
    """List user's notifications."""
    notifications = service.get_user_notifications(
        current_user.id,
        unread_only=unread_only,
        limit=limit,
        offset=offset
    )
    
    total = service.db.query(Notification).filter(
        Notification.user_id == current_user.id
    ).count()
    
    unread_count = service.db.query(Notification).filter(
        Notification.user_id == current_user.id,
        Notification.read_at == None
    ).count()
    
    return NotificationList(
        items=notifications,
        total=total,
        unread_count=unread_count
    )

@router.post("/{notification_id}/read")
async def mark_notification_read(
    notification_id: str,
    current_user: User = Depends(get_current_active_user),
    service: NotificationService = Depends(get_notification_service)
):
    """Mark a notification as read."""
    service.mark_notification_read(notification_id, current_user.id)
    return {"status": "success"}

@router.websocket("/ws")
async def notification_websocket(
    websocket: WebSocket,
    db: Session = Depends(get_db)
):
    """WebSocket endpoint for real-time notifications.
    
    Authentication Flow:
    1. Client sends auth token as first message after connection
    2. Server validates token and either accepts or rejects
    3. Normal communication proceeds
    
    This approach keeps tokens out of URLs and server logs.
    """
    try:
        # Accept connection first
        await websocket.accept()
        logger.debug("WebSocket connection accepted, waiting for authentication")
        
        # Wait for authentication message (with timeout)
        try:
            # First message must be authentication token
            auth_message = await websocket.receive_text()
            
            # Parse authentication message
            # Expected format: {"type": "auth", "token": "..."}
            import json
            auth_data = json.loads(auth_message)
            
            if auth_data.get("type") != "auth":
                await websocket.send_json({
                    "type": "error",
                    "message": "First message must be authentication"
                })
                await websocket.close(code=4001, reason="Authentication required")
                return
            
            token = auth_data.get("token", "")
            
            # Remove 'Bearer ' prefix if present
            if token.startswith('Bearer '):
                token = token[7:]
            
            # Get auth service and verify token
            auth_service = AuthService(db)
            
            try:
                user = auth_service.get_current_active_user(token)
                if not user:
                    await websocket.send_json({
                        "type": "error",
                        "message": "Invalid authentication token"
                    })
                    await websocket.close(code=4001, reason="Invalid authentication token")
                    return
            except Exception as auth_error:
                logger.error("Authentication failed", extra={"error": str(auth_error)})
                await websocket.send_json({
                    "type": "error",
                    "message": "Authentication failed"
                })
                await websocket.close(code=4001, reason=str(auth_error))
                return
            
            # Send authentication success
            await websocket.send_json({
                "type": "auth_success",
                "message": "Authenticated successfully"
            })
            logger.debug("WebSocket authenticated for user", extra={"email": user.email})
            
        except json.JSONDecodeError:
            await websocket.send_json({
                "type": "error",
                "message": "Invalid authentication message format"
            })
            await websocket.close(code=4002, reason="Invalid message format")
            return
        except Exception as e:
            logger.error("Authentication error", extra={"error": str(e)})
            await websocket.close(code=4003, reason="Authentication error")
            return
        
        # Ensure WebSocket notification preference exists
        service = NotificationService(db)
        preference = db.query(NotificationPreference).filter(
            NotificationPreference.user_id == user.id,
            NotificationPreference.channel == NotificationChannel.WEBSOCKET
        ).first()
        
        if not preference:
            logger.debug("Creating WebSocket notification preference for user", extra={"email": user.email})
            preference = NotificationPreference(
                id=str(uuid.uuid4()),
                user_id=user.id,
                channel=NotificationChannel.WEBSOCKET,
                enabled=True,
                min_priority=NotificationPriority.LOW
            )
            db.add(preference)
            db.commit()
            logger.debug("WebSocket preference created for user", extra={"email": user.email})
        
        # Register websocket
        await service.register_websocket(user.id, websocket)
        logger.debug("WebSocket registered for user", extra={"email": user.email})
        
        try:
            while True:
                # Keep connection alive
                data = await websocket.receive_text()
                logger.debug("Received WebSocket message from user", extra={"email": user.email, "data": data})
        except WebSocketDisconnect:
            # Unregister on disconnect
            await service.unregister_websocket(user.id)
            logger.debug("WebSocket disconnected for user", extra={"email": user.email})
    except Exception as e:
        logger.error("WebSocket error", extra={"error": str(e)})
        await websocket.close(code=1008, reason=str(e)) 