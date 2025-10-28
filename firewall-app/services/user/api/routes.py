"""User API routes.

This module provides FastAPI routes for user management.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from services.user.core.user_service import UserService
from services.common.database.session import get_db
from services.common.models.user import User
from services.auth.api.routes import get_current_active_user
from .schemas import (
    UserCreate,
    UserUpdate,
    UserResponse,
    UserProfileCreate,
    UserProfileResponse,
    PasswordChange,
    APIKeyResponse,
    APIKeyCreate,
    APIKeyList
)

router = APIRouter(tags=["users"])

def get_user_service(db: Session = Depends(get_db)) -> UserService:
    """Get an instance of the UserService."""
    return UserService(db)

@router.post("/", response_model=UserResponse)
async def create_user(
    user_data: UserCreate,
    db: Session = Depends(get_db)
):
    """Create a new user."""
    service = UserService(db)
    try:
        user = service.create_user(
            email=user_data.email,
            password=user_data.password,
            name=user_data.name,
        )
        return user
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_active_user)
) -> User:
    """Get current user information."""
    return current_user

@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get a specific user's information."""
    service = UserService(db)
    user = service.get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.get("/", response_model=List[UserResponse])
async def list_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """List users with optional filtering."""
    service = UserService(db)
    return service.list_users(skip=skip, limit=limit)

@router.put("/me", response_model=UserResponse)
async def update_user_info(
    user_data: UserUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> User:
    """Update current user information."""
    for field, value in user_data.dict(exclude_unset=True).items():
        setattr(current_user, field, value)
    db.commit()
    db.refresh(current_user)
    return current_user

@router.post("/me/change-password")
async def change_password(
    password_data: PasswordChange,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Change the current user's password."""
    service = UserService(db)
    try:
        success = service.change_password(
            user_id=current_user.id,
            current_password=password_data.current_password,
            new_password=password_data.new_password
        )
        if success:
            return {"message": "Password changed successfully"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/me/profile", response_model=UserProfileResponse)
async def get_current_user_profile(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get the current user's profile."""
    service = UserService(db)
    profile = service.get_profile(current_user.id)
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    return profile

@router.put("/me/profile", response_model=UserProfileResponse)
async def update_current_user_profile(
    profile_data: UserProfileCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update the current user's profile."""
    service = UserService(db)
    try:
        profile = service.create_profile(
            user_id=current_user.id,
            title=profile_data.title,
            bio=profile_data.bio,
            expertise=profile_data.expertise
        )
        return profile
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/me/api-keys", response_model=APIKeyResponse)
async def create_api_key(
    key_data: APIKeyCreate,
    current_user: User = Depends(get_current_active_user),
    service: UserService = Depends(get_user_service)
) -> APIKeyResponse:
    """Create a new API key for the current user."""
    return await service.create_api_key(
        user_id=current_user.id,
        name=key_data.name,
        expires_in_days=key_data.expires_in_days
    )

@router.get("/me/api-keys", response_model=APIKeyList)
async def list_api_keys(
    current_user: User = Depends(get_current_active_user),
    service: UserService = Depends(get_user_service)
) -> APIKeyList:
    """List all API keys for the current user."""
    keys = await service.list_api_keys(current_user.id)
    return APIKeyList(
        items=keys,
        total=len(keys)
    )

@router.post("/me/api-keys/{key_id}/revoke")
async def revoke_api_key(
    key_id: str,
    current_user: User = Depends(get_current_active_user),
    service: UserService = Depends(get_user_service)
):
    """Revoke an API key (soft delete - sets is_active=False)."""
    await service.revoke_api_key(key_id)
    return {"message": "API key revoked successfully"}

@router.post("/me/api-keys/{key_id}/regenerate", response_model=APIKeyResponse)
async def regenerate_api_key(
    key_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Regenerate an API key while keeping its metadata."""
    service = UserService(db)
    try:
        api_key = await service.regenerate_api_key(key_id, current_user.id)
        return api_key
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/me/api-keys/{key_id}")
async def delete_api_key(
    key_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Delete an API key."""
    service = UserService(db)
    try:
        await service.delete_api_key(key_id, current_user.id)
        return {"message": "API key deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/me/api-keys/{key_id}/deactivate", response_model=APIKeyResponse)
async def deactivate_api_key(
    key_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Deactivate an API key."""
    service = UserService(db)
    try:
        api_key = await service.deactivate_api_key(key_id, current_user.id)
        return api_key
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/me/api-keys/{key_id}/activate", response_model=APIKeyResponse)
async def activate_api_key(
    key_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Activate an API key."""
    service = UserService(db)
    try:
        api_key = await service.activate_api_key(key_id, current_user.id)
        return api_key
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) 