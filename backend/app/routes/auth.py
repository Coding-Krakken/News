"""
Authentication routes for user registration, login, and token management.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from typing import List

from ..database import get_database
from ..models.schemas import User, UserCreate, UserUpdate, UserInDB, Token, UserRole
from ..utils.auth import (
    verify_password,
    get_password_hash,
    create_access_token,
    create_refresh_token,
    decode_token,
)
from ..utils.dependencies import get_current_active_user, get_current_admin_user
from ..utils.rate_limit import limiter, get_rate_limit

router = APIRouter()


@router.post("/register", response_model=User, status_code=status.HTTP_201_CREATED)
@limiter.limit(get_rate_limit("auth_register"))
async def register(request: Request, user_data: UserCreate):
    """Register a new user."""
    db = get_database()

    # Check if username already exists
    existing_user = await db.users.find_one({"username": user_data.username})
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered",
        )

    # Check if email already exists
    existing_email = await db.users.find_one({"email": user_data.email})
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered"
        )

    # Create user
    hashed_password = get_password_hash(user_data.password)
    user_dict = user_data.model_dump(exclude={"password"})
    user_dict["hashed_password"] = hashed_password
    user_dict["role"] = UserRole.USER  # Default role

    user_in_db = UserInDB(**user_dict)

    # Insert into database
    await db.users.insert_one(user_in_db.model_dump())

    # Return user without password
    return User(**user_dict)


@router.post("/login", response_model=Token)
@limiter.limit(get_rate_limit("auth_login"))
async def login(request: Request, form_data: OAuth2PasswordRequestForm = Depends()):
    """Login and get access token."""
    db = get_database()

    # Find user
    user_data = await db.users.find_one({"username": form_data.username})
    if not user_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Verify password
    if not verify_password(form_data.password, user_data["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Create tokens
    access_token = create_access_token(
        data={"sub": user_data["username"], "role": user_data.get("role", "user")}
    )
    refresh_token = create_refresh_token(data={"sub": user_data["username"]})

    return Token(access_token=access_token, refresh_token=refresh_token)


@router.post("/refresh", response_model=Token)
@limiter.limit(get_rate_limit("auth_refresh"))
async def refresh_token(request: Request, refresh_token: str):
    """Refresh access token using refresh token."""
    payload = decode_token(refresh_token)

    if payload is None or payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token"
        )

    username = payload.get("sub")
    if not username:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token"
        )

    # Get user to get current role
    db = get_database()
    user_data = await db.users.find_one({"username": username})
    if not user_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found"
        )

    # Create new tokens
    access_token = create_access_token(
        data={"sub": username, "role": user_data.get("role", "user")}
    )
    new_refresh_token = create_refresh_token(data={"sub": username})

    return Token(access_token=access_token, refresh_token=new_refresh_token)


@router.get("/me", response_model=User)
async def get_current_user_profile(
    current_user: User = Depends(get_current_active_user),
):
    """Get current user profile."""
    return current_user


@router.put("/me", response_model=User)
async def update_current_user_profile(
    user_update: UserUpdate, current_user: User = Depends(get_current_active_user)
):
    """Update current user profile."""
    db = get_database()

    # Prepare update data
    update_data = user_update.model_dump(exclude_unset=True)
    if not update_data:
        return current_user

    # Check if email is being changed and if it's already in use
    if "email" in update_data:
        existing_email = await db.users.find_one(
            {"email": update_data["email"], "username": {"$ne": current_user.username}}
        )
        if existing_email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Email already in use"
            )

    # Update user
    from datetime import datetime

    update_data["updated_at"] = datetime.utcnow()

    await db.users.update_one(
        {"username": current_user.username}, {"$set": update_data}
    )

    # Return updated user
    updated_user = await db.users.find_one({"username": current_user.username})
    updated_user.pop("hashed_password", None)
    updated_user.pop("_id", None)

    return User(**updated_user)


@router.post("/me/bookmarks/stories/{story_id}")
async def bookmark_story(
    story_id: str, current_user: User = Depends(get_current_active_user)
):
    """Bookmark a story."""
    db = get_database()

    await db.users.update_one(
        {"username": current_user.username},
        {"$addToSet": {"bookmarked_stories": story_id}},
    )

    return {"message": "Story bookmarked successfully"}


@router.delete("/me/bookmarks/stories/{story_id}")
async def unbookmark_story(
    story_id: str, current_user: User = Depends(get_current_active_user)
):
    """Remove story bookmark."""
    db = get_database()

    await db.users.update_one(
        {"username": current_user.username}, {"$pull": {"bookmarked_stories": story_id}}
    )

    return {"message": "Story bookmark removed"}


@router.get("/me/bookmarks/stories", response_model=List[str])
async def get_bookmarked_stories(current_user: User = Depends(get_current_active_user)):
    """Get bookmarked stories."""
    return current_user.bookmarked_stories


# Admin routes
@router.get("/users", response_model=List[User])
async def list_users(
    skip: int = 0, limit: int = 50, current_user: User = Depends(get_current_admin_user)
):
    """List all users (admin only)."""
    db = get_database()

    cursor = db.users.find({}).skip(skip).limit(limit)
    users = await cursor.to_list(length=limit)

    # Remove sensitive data
    for user in users:
        user.pop("hashed_password", None)
        user.pop("_id", None)

    return [User(**user) for user in users]


@router.put("/users/{username}/role")
async def update_user_role(
    username: str, role: UserRole, current_user: User = Depends(get_current_admin_user)
):
    """Update user role (admin only)."""
    db = get_database()

    result = await db.users.update_one({"username": username}, {"$set": {"role": role}})

    if result.matched_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    return {"message": f"User role updated to {role}"}


@router.put("/users/{username}/disable")
async def disable_user(
    username: str, current_user: User = Depends(get_current_admin_user)
):
    """Disable user account (admin only)."""
    db = get_database()

    result = await db.users.update_one(
        {"username": username}, {"$set": {"disabled": True}}
    )

    if result.matched_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    return {"message": "User disabled successfully"}
