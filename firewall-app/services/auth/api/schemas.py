"""Authentication API schemas.

This module defines Pydantic models for authentication endpoints.
"""

from pydantic import BaseModel

class Token(BaseModel):
    """Schema for access token response."""
    access_token: str
    token_type: str

class TokenData(BaseModel):
    """Schema for decoded token data."""
    user_id: str
    email: str
