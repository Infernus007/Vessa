"""User API schemas.

This module defines request and response models for the user management API.
"""

from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field, constr

class UserBase(BaseModel):
    """Base model for users."""
    email: EmailStr
    name: constr(min_length=2, max_length=100)

class UserCreate(UserBase):
    """Model for user creation requests."""
    password: constr(min_length=8)

class UserUpdate(BaseModel):
    """Model for user update requests."""
    name: Optional[constr(min_length=2, max_length=100)] = None
    email: Optional[EmailStr] = None

class UserResponse(UserBase):
    """Model for user responses."""
    id: str
    is_active: bool
    is_superuser: bool
    created_at: datetime
    updated_at: datetime
    last_login: Optional[datetime] = None
    profile: Optional['UserProfileResponse'] = None

    class Config:
        from_attribute = True

class PasswordChange(BaseModel):
    """Model for password change requests."""
    current_password: str
    new_password: constr(min_length=8)

class UserProfileBase(BaseModel):
    """Base model for user profiles."""
    first_name: Optional[str] = Field(None, max_length=50)
    last_name: Optional[str] = Field(None, max_length=50)
    phone: Optional[str] = Field(None, max_length=20)
    department: Optional[str] = Field(None, max_length=100)
    role: Optional[str] = Field(None, max_length=100)
    avatar_url: Optional[str] = Field(None, max_length=255)
    bio: Optional[str] = None

class UserProfileCreate(UserProfileBase):
    """Model for profile creation/update requests."""
    pass

class UserProfileResponse(UserProfileBase):
    """Model for profile responses."""
    id: str
    user_id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attribute = True

class APIKeyCreate(BaseModel):
    """Schema for creating a new API key."""
    name: str = Field(..., min_length=1, max_length=255)
    expires_in_days: Optional[int] = Field(None, ge=1)

class APIKeyResponse(BaseModel):
    """Schema for API key response."""
    id: str
    name: str
    key: str
    is_active: bool
    created_at: datetime
    expires_at: Optional[datetime] = None
    last_used_at: Optional[datetime] = None
    revoked_at: Optional[datetime] = None

    model_config = {
        "from_attributes": True
    }

class APIKeyList(BaseModel):
    """Schema for list of API keys."""
    items: List[APIKeyResponse]
    total: int 