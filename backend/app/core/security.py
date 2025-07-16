"""
Smart Home IoT Backend - Security Module
=======================================

This module provides security utilities including JWT token handling,
password hashing, and authentication functions.
"""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import jwt
from passlib.context import CryptContext
from fastapi import HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi import Depends
import secrets
import structlog

from app.core.config import settings

logger = structlog.get_logger(__name__)

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT Bearer token scheme
security = HTTPBearer()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plain password against a hashed password.
    
    Args:
        plain_password: Plain text password
        hashed_password: Hashed password
        
    Returns:
        bool: True if password matches, False otherwise
    """
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except Exception as e:
        logger.error(f"Password verification failed: {e}")
        return False


def get_password_hash(password: str) -> str:
    """
    Hash a password using bcrypt.
    
    Args:
        password: Plain text password
        
    Returns:
        str: Hashed password
    """
    try:
        return pwd_context.hash(password)
    except Exception as e:
        logger.error(f"Password hashing failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to hash password"
        )


def generate_random_token(length: int = 32) -> str:
    """
    Generate a random token for various purposes.
    
    Args:
        length: Length of the token
        
    Returns:
        str: Random token
    """
    return secrets.token_urlsafe(length)


def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT access token.
    
    Args:
        data: Data to encode in the token
        expires_delta: Optional expiration time delta
        
    Returns:
        str: JWT access token
    """
    try:
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        
        to_encode.update({"exp": expire})
        to_encode.update({"iat": datetime.utcnow()})
        to_encode.update({"type": "access"})
        
        encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        return encoded_jwt
        
    except Exception as e:
        logger.error(f"Failed to create access token: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create access token"
        )


def create_refresh_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT refresh token.
    
    Args:
        data: Data to encode in the token
        expires_delta: Optional expiration time delta
        
    Returns:
        str: JWT refresh token
    """
    try:
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        
        to_encode.update({"exp": expire})
        to_encode.update({"iat": datetime.utcnow()})
        to_encode.update({"type": "refresh"})
        
        encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        return encoded_jwt
        
    except Exception as e:
        logger.error(f"Failed to create refresh token: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create refresh token"
        )


def verify_token(token: str, expected_type: str = "access") -> Dict[str, Any]:
    """
    Verify and decode a JWT token.
    
    Args:
        token: JWT token to verify
        expected_type: Expected token type (access or refresh)
        
    Returns:
        Dict[str, Any]: Decoded token payload
        
    Raises:
        HTTPException: If token is invalid or expired
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        
        # Check token type
        token_type = payload.get("type")
        if token_type != expected_type:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Invalid token type. Expected {expected_type}, got {token_type}",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Check expiration
        exp = payload.get("exp")
        if exp is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has no expiration",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        if datetime.utcfromtimestamp(exp) < datetime.utcnow():
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        return payload
        
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception as e:
        logger.error(f"Token verification failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


def get_current_user_from_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict[str, Any]:
    """
    Get current user from JWT token.
    
    Args:
        credentials: HTTP authorization credentials
        
    Returns:
        Dict[str, Any]: User information from token
    """
    token = credentials.credentials
    payload = verify_token(token, "access")
    
    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return {
        "user_id": user_id,
        "username": payload.get("username"),
        "email": payload.get("email"),
        "role": payload.get("role", "user"),
        "token_data": payload
    }


def create_token_pair(user_data: Dict[str, Any]) -> Dict[str, str]:
    """
    Create both access and refresh tokens for a user.
    
    Args:
        user_data: User data to encode in tokens
        
    Returns:
        Dict[str, str]: Dictionary containing access and refresh tokens
    """
    try:
        # Prepare token data
        token_data = {
            "sub": str(user_data["user_id"]),
            "username": user_data.get("username"),
            "email": user_data.get("email"),
            "role": user_data.get("role", "user")
        }
        
        # Create tokens
        access_token = create_access_token(token_data)
        refresh_token = create_refresh_token(token_data)
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer"
        }
        
    except Exception as e:
        logger.error(f"Failed to create token pair: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create authentication tokens"
        )


def refresh_access_token(refresh_token: str) -> str:
    """
    Create a new access token using a refresh token.
    
    Args:
        refresh_token: Valid refresh token
        
    Returns:
        str: New access token
    """
    try:
        # Verify refresh token
        payload = verify_token(refresh_token, "refresh")
        
        # Create new access token with same data
        token_data = {
            "sub": payload["sub"],
            "username": payload.get("username"),
            "email": payload.get("email"),
            "role": payload.get("role", "user")
        }
        
        return create_access_token(token_data)
        
    except Exception as e:
        logger.error(f"Failed to refresh access token: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not refresh access token",
            headers={"WWW-Authenticate": "Bearer"},
        )


def validate_password_strength(password: str) -> Dict[str, Any]:
    """
    Validate password strength requirements.
    
    Args:
        password: Password to validate
        
    Returns:
        Dict[str, Any]: Validation result with is_valid flag and messages
    """
    result = {
        "is_valid": True,
        "messages": [],
        "requirements": {
            "min_length": False,
            "has_uppercase": False,
            "has_lowercase": False,
            "has_digit": False,
            "has_special": False
        }
    }
    
    # Check minimum length
    if len(password) >= 8:
        result["requirements"]["min_length"] = True
    else:
        result["is_valid"] = False
        result["messages"].append("Password must be at least 8 characters long")
    
    # Check for uppercase letter
    if any(c.isupper() for c in password):
        result["requirements"]["has_uppercase"] = True
    else:
        result["is_valid"] = False
        result["messages"].append("Password must contain at least one uppercase letter")
    
    # Check for lowercase letter
    if any(c.islower() for c in password):
        result["requirements"]["has_lowercase"] = True
    else:
        result["is_valid"] = False
        result["messages"].append("Password must contain at least one lowercase letter")
    
    # Check for digit
    if any(c.isdigit() for c in password):
        result["requirements"]["has_digit"] = True
    else:
        result["is_valid"] = False
        result["messages"].append("Password must contain at least one digit")
    
    # Check for special character
    special_chars = "!@#$%^&*()_+-=[]{}|;:,.<>?"
    if any(c in special_chars for c in password):
        result["requirements"]["has_special"] = True
    else:
        result["is_valid"] = False
        result["messages"].append("Password must contain at least one special character")
    
    return result


def sanitize_user_data(user_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Sanitize user data for public consumption (remove sensitive fields).
    
    Args:
        user_data: Raw user data
        
    Returns:
        Dict[str, Any]: Sanitized user data
    """
    sensitive_fields = ["password", "hashed_password", "password_hash", "secret_key"]
    
    return {
        key: value for key, value in user_data.items()
        if key not in sensitive_fields
    }


def check_rate_limit(user_id: str, action: str, limit: int, window_seconds: int = 60) -> bool:
    """
    Simple rate limiting check (placeholder - would need Redis in production).
    
    Args:
        user_id: User identifier
        action: Action being performed
        limit: Maximum number of actions allowed
        window_seconds: Time window in seconds
        
    Returns:
        bool: True if within rate limit, False otherwise
    """
    # This is a placeholder implementation
    # In a real application, you would use Redis or another cache
    # to track requests per user per action
    
    # For now, always return True (no rate limiting)
    return True


def generate_api_key(user_id: str) -> str:
    """
    Generate an API key for a user.
    
    Args:
        user_id: User identifier
        
    Returns:
        str: Generated API key
    """
    import hashlib
    
    # Create a unique API key
    timestamp = str(datetime.utcnow().timestamp())
    raw_key = f"{user_id}:{timestamp}:{settings.SECRET_KEY}"
    
    # Hash the raw key
    api_key = hashlib.sha256(raw_key.encode()).hexdigest()
    
    return f"sha_{api_key[:32]}"


def verify_api_key(api_key: str, user_id: str) -> bool:
    """
    Verify an API key for a user.
    
    Args:
        api_key: API key to verify
        user_id: User identifier
        
    Returns:
        bool: True if API key is valid, False otherwise
    """
    # This is a placeholder implementation
    # In a real application, you would store API keys in a database
    # and verify them against stored values
    
    # For now, just check if the API key has the correct format
    return api_key.startswith("sha_") and len(api_key) == 36


# Security dependency functions
async def get_current_user(current_user: Dict[str, Any] = Depends(get_current_user_from_token)) -> Dict[str, Any]:
    """
    Get current authenticated user.
    
    Args:
        current_user: Current user from token
        
    Returns:
        Dict[str, Any]: Current user data
    """
    return current_user


async def get_current_admin_user(current_user: Dict[str, Any] = Depends(get_current_user)) -> Dict[str, Any]:
    """
    Get current authenticated admin user.
    
    Args:
        current_user: Current user from token
        
    Returns:
        Dict[str, Any]: Current admin user data
        
    Raises:
        HTTPException: If user is not an admin
    """
    if current_user.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user 