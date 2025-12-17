"""
FastAPI dependencies for authentication and authorization.
"""
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from typing import Optional
from ..models.schemas import User, UserInDB, TokenData, UserRole
from ..database import get_database
from .auth import decode_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login")


async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    """Get current authenticated user from JWT token."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    payload = decode_token(token)
    if payload is None:
        raise credentials_exception
    
    username: str = payload.get("sub")
    if username is None:
        raise credentials_exception
    
    # Get user from database
    db = get_database()
    user_data = await db.users.find_one({"username": username})
    
    if user_data is None:
        raise credentials_exception
    
    # Remove sensitive data
    user_data.pop("hashed_password", None)
    user_data.pop("_id", None)
    
    return User(**user_data)


async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """Get current active user (not disabled)."""
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


async def get_current_admin_user(
    current_user: User = Depends(get_current_active_user)
) -> User:
    """Get current admin user (RBAC check)."""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions. Admin access required."
        )
    return current_user


# Optional authentication (doesn't raise exception if not authenticated)
async def get_optional_user(token: Optional[str] = Depends(oauth2_scheme)) -> Optional[User]:
    """Get current user if authenticated, otherwise None."""
    if token is None:
        return None
    try:
        return await get_current_user(token)
    except HTTPException:
        return None
