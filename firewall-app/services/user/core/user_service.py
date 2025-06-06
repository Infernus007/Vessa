"""User management service.

This module provides functionality for managing users and their profiles.
"""

from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
import secrets
import string
from sqlalchemy import or_, and_
from sqlalchemy.exc import IntegrityError

from services.common.models.user import User, UserProfile, APIKey
from services.common.utils import generate_uuid
from services.common.security import get_password_hash, verify_password

def generate_api_key() -> str:
    """Generate a secure API key.
    
    Returns:
        A 48-character secure random string
    """
    prefix = 'vk'  # vessa key prefix
    alphabet = string.ascii_letters + string.digits
    random_part = ''.join(secrets.choice(alphabet) for _ in range(46))
    return f"{prefix}_{random_part}"

class UserService:
    """Service for managing users and their profiles."""

    def __init__(self, db: Session):
        """Initialize the service.
        
        Args:
            db: Database session
        """
        self.db = db

    def create_user(
        self,
        email: str,
        password: str,
        name: str,
        role: str = "client"
    ) -> User:
        """Create a new user.
        
        Args:
            email: User's email
            password: User's password
            name: User's name
            role: User's role (default: client)
            
        Returns:
            Created user
            
        Raises:
            HTTPException: If email already exists
        """
        if self.get_user_by_email(email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )

        # Create user
        user_id = generate_uuid()
        hashed_password = get_password_hash(password)
        user = User(
            id=user_id,
            email=email,
            name=name,
            password_hash=hashed_password,
            is_active=True,
            created_at=datetime.utcnow()
        )
        
        # Create default profile
        first_name = name.split()[0] if name else None
        last_name = " ".join(name.split()[1:]) if name and len(name.split()) > 1 else None
        
        profile = UserProfile(
            id=generate_uuid(),
            user_id=user_id,
            first_name=first_name,
            last_name=last_name,
            created_at=datetime.utcnow()
        )
        
        user.profile = profile
        
        try:
            self.db.add(user)
            self.db.commit()
            self.db.refresh(user)
            return user
        except IntegrityError as e:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Database error occurred while creating user"
            ) from e

    def get_user(self, user_id: str) -> Optional[User]:
        """Get a user by ID.
        
        Args:
            user_id: User's ID
            
        Returns:
            User if found, None otherwise
        """
        return self.db.query(User).filter(User.id == user_id).first()

    def get_user_by_email(self, email: str) -> Optional[User]:
        """Get a user by email.
        
        Args:
            email: User's email
            
        Returns:
            User if found, None otherwise
        """
        return self.db.query(User).filter(User.email == email).first()

    def get_user_by_id(self, user_id: str) -> Optional[User]:
        """Get a user by their ID. Alias for get_user for backward compatibility.
        
        Args:
            user_id: User's ID
            
        Returns:
            User if found, None otherwise
        """
        return self.get_user(user_id)

    async def validate_api_key(self, api_key: str) -> bool:
        """Validate an API key.
        
        Args:
            api_key: The API key to validate
            
        Returns:
            bool: True if the API key is valid and active, False otherwise
        """
        key = self.db.query(APIKey).filter(
            and_(
                APIKey.key == api_key,
                APIKey.is_active == True,
                or_(
                    APIKey.expires_at.is_(None),
                    APIKey.expires_at > datetime.utcnow()
                )
            )
        ).first()
        
        return key is not None

    async def get_api_key(self, api_key: str) -> APIKey:
        """Get an API key object.
        
        Args:
            api_key: The API key to retrieve
            
        Returns:
            APIKey: The API key object if found and valid
            
        Raises:
            HTTPException: If API key is not found or is invalid
        """
        key = self.db.query(APIKey).filter(
            and_(
                APIKey.key == api_key,
                APIKey.is_active == True,
                or_(
                    APIKey.expires_at.is_(None),
                    APIKey.expires_at > datetime.utcnow()
                )
            )
        ).first()
        
        if not key:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired API key"
            )
            
        return key

    async def create_api_key(
        self, 
        user_id: str,
        name: str,
        expires_in_days: Optional[int] = None
    ) -> APIKey:
        """Create a new API key for a user.
        
        Args:
            user_id: ID of the user to create the key for
            name: Name/description of the API key
            expires_in_days: Optional number of days until key expires
            
        Returns:
            APIKey: The created API key object
            
        Raises:
            HTTPException: If user not found or validation fails
        """
        # Verify user exists
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
            
        # Calculate expiration if provided
        expires_at = None
        if expires_in_days:
            expires_at = datetime.utcnow() + timedelta(days=expires_in_days)
            
        # Create API key
        api_key = APIKey(
            id=generate_uuid(),
            user_id=user_id,
            key=f"vk_{generate_uuid()}",
            name=name,
            expires_at=expires_at,
            is_active=True,
            created_at=datetime.utcnow()
        )
        
        self.db.add(api_key)
        self.db.commit()
        self.db.refresh(api_key)
        
        return api_key

    async def list_api_keys(self, user_id: str) -> List[APIKey]:
        """List all API keys for a user.
        
        Args:
            user_id: ID of the user to list keys for
            
        Returns:
            List[APIKey]: List of API key objects
            
        Raises:
            HTTPException: If user not found
        """
        # Verify user exists
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
            
        return self.db.query(APIKey).filter(APIKey.user_id == user_id).all()

    async def revoke_api_key(self, key_id: str) -> None:
        """Revoke an API key.
        
        Args:
            key_id: ID of the API key to revoke
            
        Raises:
            HTTPException: If API key not found
        """
        key = self.db.query(APIKey).filter(APIKey.id == key_id).first()
        if not key:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="API key not found"
            )
            
        key.is_active = False
        key.revoked_at = datetime.utcnow()
        self.db.commit()

    def create_profile(
        self,
        user_id: str,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        phone: Optional[str] = None,
        department: Optional[str] = None,
        role: Optional[str] = None,
        avatar_url: Optional[str] = None,
        bio: Optional[str] = None
    ) -> UserProfile:
        """Create or update a user's profile.
        
        Args:
            user_id: User's ID
            first_name: First name
            last_name: Last name
            phone: Phone number
            department: Department
            role: Role
            avatar_url: Avatar URL
            bio: User biography
            
        Returns:
            Created or updated profile
            
        Raises:
            HTTPException: If user not found
        """
        user = self.get_user(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        profile = self.db.query(UserProfile).filter(
            UserProfile.user_id == user_id
        ).first()

        if not profile:
            profile = UserProfile(
                id=generate_uuid(),
                user_id=user_id,
                first_name=first_name,
                last_name=last_name,
                phone=phone,
                department=department,
                role=role,
                avatar_url=avatar_url,
                bio=bio,
                created_at=datetime.utcnow()
            )
            self.db.add(profile)
        else:
            if first_name is not None:
                profile.first_name = first_name
            if last_name is not None:
                profile.last_name = last_name
            if phone is not None:
                profile.phone = phone
            if department is not None:
                profile.department = department
            if role is not None:
                profile.role = role
            if avatar_url is not None:
                profile.avatar_url = avatar_url
            if bio is not None:
                profile.bio = bio
            profile.updated_at = datetime.utcnow()

        self.db.commit()
        self.db.refresh(profile)
        return profile

    def get_profile(self, user_id: str) -> Optional[UserProfile]:
        """Get a user's profile.
        
        Args:
            user_id: User's ID
            
        Returns:
            User profile if found, None otherwise
        """
        return self.db.query(UserProfile).filter(
            UserProfile.user_id == user_id
        ).first()

    def update_user(
        self,
        user_id: str,
        name: Optional[str] = None,
        email: Optional[str] = None,
        is_active: Optional[bool] = None
    ) -> User:
        """Update a user's information.
        
        Args:
            user_id: User's ID
            name: New name
            email: New email
            is_active: New active status
            
        Returns:
            Updated user
            
        Raises:
            HTTPException: If user not found or email exists
        """
        user = self.get_user(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        if email and email != user.email:
            if self.get_user_by_email(email):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already registered"
                )
            user.email = email

        if name:
            user.name = name
      
        if is_active is not None:
            user.is_active = is_active

        self.db.commit()
        self.db.refresh(user)
        return user

    def change_password(
        self,
        user_id: str,
        current_password: str,
        new_password: str
    ) -> bool:
        """Change a user's password.
        
        Args:
            user_id: User's ID
            current_password: Current password
            new_password: New password
            
        Returns:
            True if successful
            
        Raises:
            HTTPException: If user not found or current password is incorrect
        """
        user = self.get_user(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        if not verify_password(current_password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Current password is incorrect"
            )

        user.password_hash = get_password_hash(new_password)
        self.db.commit()
        return True

    def list_users(
        self,
        skip: int = 0,
        limit: int = 100,
    ) -> List[User]:
        """List users with optional filtering.
        
        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of users
        """
        query = self.db.query(User)
       
        return query.offset(skip).limit(limit).all() 