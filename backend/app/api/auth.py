"""
Smart Home IoT Backend - Authentication API
==========================================

This module contains authentication endpoints for login, registration,
and token management.
"""

from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr
from typing import Optional, Dict, Any
import structlog
from datetime import datetime

from app.core.security import (
    verify_password,
    get_password_hash,
    create_token_pair,
    refresh_access_token,
    get_current_user,
    validate_password_strength,
    sanitize_user_data,
    security
)

logger = structlog.get_logger(__name__)

router = APIRouter()


# Pydantic models for request/response
class UserLogin(BaseModel):
    username: str
    password: str


class UserRegister(BaseModel):
    username: str
    email: EmailStr
    password: str
    full_name: Optional[str] = None


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int = 1800  # 30 minutes


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class UserResponse(BaseModel):
    user_id: str
    username: str
    email: str
    full_name: Optional[str]
    role: str
    created_at: str
    is_active: bool


# Mock user database (in production, this would be a real database)
MOCK_USERS = {
    "admin": {
        "user_id": "1",
        "username": "admin",
        "email": "admin@smarthome.local",
        "full_name": "Administrator",
        "role": "admin",
        "password_hash": get_password_hash("admin123"),
        "created_at": "2024-01-01T00:00:00Z",
        "is_active": True
    },
    "user": {
        "user_id": "2",
        "username": "user",
        "email": "user@smarthome.local",
        "full_name": "Regular User",
        "role": "user",
        "password_hash": get_password_hash("user123"),
        "created_at": "2024-01-01T00:00:00Z",
        "is_active": True
    }
}


def get_user_by_username(username: str) -> Optional[Dict[str, Any]]:
    """Get user by username from mock database."""
    return MOCK_USERS.get(username)


def get_user_by_id(user_id: str) -> Optional[Dict[str, Any]]:
    """Get user by ID from mock database."""
    for user in MOCK_USERS.values():
        if user["user_id"] == user_id:
            return user
    return None


@router.post("/login", response_model=TokenResponse)
async def login(credentials: UserLogin):
    """
    User login endpoint.
    
    Args:
        credentials: Login credentials
        
    Returns:
        TokenResponse: JWT tokens
    """
    try:
        # Get user from database
        user = get_user_by_username(credentials.username)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Verify password
        if not verify_password(credentials.password, user["password_hash"]):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Check if user is active
        if not user.get("is_active", True):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User account is disabled",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Create token pair
        token_data = create_token_pair(user)
        
        logger.info(f"User {credentials.username} logged in successfully")
        
        return TokenResponse(
            access_token=token_data["access_token"],
            refresh_token=token_data["refresh_token"],
            token_type=token_data["token_type"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during login"
        )


@router.post("/register", response_model=UserResponse)
async def register(user_data: UserRegister):
    """
    User registration endpoint.
    
    Args:
        user_data: Registration data
        
    Returns:
        UserResponse: Created user data
    """
    try:
        # Check if user already exists
        if get_user_by_username(user_data.username):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already exists"
            )
        
        # Validate password strength
        password_validation = validate_password_strength(user_data.password)
        if not password_validation["is_valid"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "message": "Password does not meet requirements",
                    "requirements": password_validation["requirements"],
                    "errors": password_validation["messages"]
                }
            )
        
        # Create new user
        new_user = {
            "user_id": str(len(MOCK_USERS) + 1),
            "username": user_data.username,
            "email": user_data.email,
            "full_name": user_data.full_name,
            "role": "user",
            "password_hash": get_password_hash(user_data.password),
            "created_at": datetime.utcnow().isoformat(),
            "is_active": True
        }
        
        # Save user to mock database
        MOCK_USERS[user_data.username] = new_user
        
        logger.info(f"User {user_data.username} registered successfully")
        
        return UserResponse(**sanitize_user_data(new_user))
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Registration failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during registration"
        )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(request: RefreshTokenRequest):
    """
    Refresh access token endpoint.
    
    Args:
        request: Refresh token request
        
    Returns:
        TokenResponse: New access token
    """
    try:
        # Create new access token
        new_access_token = refresh_access_token(request.refresh_token)
        
        return TokenResponse(
            access_token=new_access_token,
            refresh_token=request.refresh_token,  # Keep the same refresh token
            token_type="bearer"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Token refresh failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during token refresh"
        )


@router.get("/me", response_model=UserResponse)
async def get_current_user_profile(current_user: Dict[str, Any] = Depends(get_current_user)):
    """
    Get current user profile.
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        UserResponse: User profile data
    """
    try:
        # Get full user data from database
        user = get_user_by_id(current_user["user_id"])
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        return UserResponse(**sanitize_user_data(user))
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get user profile: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.post("/logout")
async def logout(current_user: Dict[str, Any] = Depends(get_current_user)):
    """
    User logout endpoint.
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        dict: Logout confirmation
    """
    try:
        # In a real application, you would add the token to a blacklist
        # For now, we'll just return a success message
        
        logger.info(f"User {current_user['username']} logged out")
        
        return {
            "message": "Successfully logged out",
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Logout failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during logout"
        )


@router.get("/verify-token")
async def verify_token(current_user: Dict[str, Any] = Depends(get_current_user)):
    """
    Verify token endpoint.
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        dict: Token verification result
    """
    return {
        "valid": True,
        "user_id": current_user["user_id"],
        "username": current_user["username"],
        "role": current_user["role"],
        "timestamp": datetime.utcnow().isoformat()
    } 