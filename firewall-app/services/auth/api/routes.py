"""Authentication API routes.

This module provides FastAPI routes for authentication endpoints.
"""

from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from services.auth.core.auth_service import AuthService, ACCESS_TOKEN_EXPIRE_MINUTES
from services.common.database.session import get_db
from services.common.models.user import User
from services.user.core.user_service import UserService
from services.user.api.schemas import UserCreate, UserResponse, PasswordChange
from services.common.audit import get_audit_logger
from .schemas import Token, TokenData

router = APIRouter()  # No prefix, it's added in main.py
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")

def get_auth_service(db: Session = Depends(get_db)) -> AuthService:
    """Get AuthService instance."""
    return AuthService(db)

@router.post("/token", response_model=Token)
async def login_for_access_token(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    auth_service: AuthService = Depends(get_auth_service),
    db: Session = Depends(get_db)
):
    """Login endpoint to get access token."""
    audit_logger = get_audit_logger(db)
    
    user = auth_service.authenticate_user(form_data.username, form_data.password)
    
    # Get client IP and user agent
    ip_address = request.client.host if request.client else "unknown"
    user_agent = request.headers.get("user-agent", "unknown")
    
    if not user:
        # Log failed login attempt
        audit_logger.log_login_failure(
            email=form_data.username,
            ip_address=ip_address,
            reason="Incorrect email or password"
        )
        
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Log successful login
    audit_logger.log_login_success(
        user_id=user.id,
        user_email=user.email,
        ip_address=ip_address,
        user_agent=user_agent
    )
        
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth_service.create_access_token(
        data={"sub": user.id, "email": user.email},
        expires_delta=access_token_expires
    )
    
    return Token(access_token=access_token, token_type="bearer")

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    auth_service: AuthService = Depends(get_auth_service)
) -> User:
    """Get current authenticated user from token."""
    user = auth_service.get_current_user(token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user

async def get_current_active_user(
    token: str = Depends(oauth2_scheme),
    auth_service: AuthService = Depends(get_auth_service)
) -> User:
    """Get current active user."""
    return auth_service.get_current_active_user(token)

@router.post("/register", response_model=UserResponse)
async def register_user(
    user_data: UserCreate,
    db: Session = Depends(get_db)
):
    """Register a new user."""
    user_service = UserService(db)
    try:
        # Check for duplicate email
        existing_user = db.query(User).filter(User.email == user_data.email).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
            
        user = user_service.create_user(
            email=user_data.email,
            password=user_data.password,
            name=user_data.name,
        )
        db.refresh(user)
        return user
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.post("/change-password", response_model=dict)
async def change_password(
    password_data: PasswordChange,
    current_user: User = Depends(get_current_active_user),
    auth_service: AuthService = Depends(get_auth_service)
):
    """Change user password."""
    success = auth_service.change_password(
        user_id=current_user.id,
        current_password=password_data.current_password,
        new_password=password_data.new_password
    )
    
    if success:
        return {"message": "Password changed successfully"}
    return {"message": "Failed to change password"} 