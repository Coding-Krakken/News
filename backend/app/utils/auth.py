"""
Authentication utilities for JWT token generation and password hashing.
"""
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
import hashlib

from ..config import get_settings

# Password hashing
# Use PBKDF2-SHA256 to avoid dependency issues with bcrypt in test environments
# and to avoid bcrypt's 72-byte password limitation.
pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")


def _get_jwt_settings():
    """Get JWT settings from config."""
    settings = get_settings()
    return settings.secret_key, settings.algorithm, settings.access_token_expire_minutes


# JWT settings
REFRESH_TOKEN_EXPIRE_DAYS = 7


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against a hash."""
    # Pre-hash the incoming plain password with SHA-256 to avoid bcrypt
    # 72-byte limitation and to provide a fixed-length input.
    prehashed = hashlib.sha256(plain_password.encode("utf-8")).hexdigest()
    return pwd_context.verify(prehashed, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash a password.

    Pre-hash the password with SHA-256 before bcrypt to handle
    arbitrary-length passwords and avoid bcrypt's 72-byte limit.
    """
    prehashed = hashlib.sha256(password.encode("utf-8")).hexdigest()
    return pwd_context.hash(prehashed)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT access token."""
    secret_key, algorithm, access_token_expire_minutes = _get_jwt_settings()
    
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=access_token_expire_minutes)
    
    to_encode.update({"exp": expire, "type": "access"})
    encoded_jwt = jwt.encode(to_encode, secret_key, algorithm=algorithm)
    return encoded_jwt


def create_refresh_token(data: dict) -> str:
    """Create JWT refresh token."""
    secret_key, algorithm, _ = _get_jwt_settings()
    
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})
    encoded_jwt = jwt.encode(to_encode, secret_key, algorithm=algorithm)
    return encoded_jwt


def decode_token(token: str) -> Optional[dict]:
    """Decode and verify JWT token."""
    secret_key, algorithm, _ = _get_jwt_settings()
    
    try:
        payload = jwt.decode(token, secret_key, algorithms=[algorithm])
        return payload
    except JWTError:
        return None
