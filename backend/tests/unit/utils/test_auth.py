"""
Unit tests for authentication utilities.
"""

from datetime import timedelta
from app.utils.auth import (
    verify_password,
    get_password_hash,
    create_access_token,
    create_refresh_token,
    decode_token,
)


class TestPasswordHashing:
    """Test password hashing functions."""

    def test_hash_password(self):
        """Test password hashing."""
        password = "TestPassword123!"
        hashed = get_password_hash(password)
        assert hashed is not None
        assert hashed != password
        assert len(hashed) > 20

    def test_verify_password_correct(self):
        """Test password verification with correct password."""
        password = "TestPassword123!"
        hashed = get_password_hash(password)
        assert verify_password(password, hashed) is True

    def test_verify_password_incorrect(self):
        """Test password verification with incorrect password."""
        password = "TestPassword123!"
        wrong_password = "WrongPassword456!"
        hashed = get_password_hash(password)
        assert verify_password(wrong_password, hashed) is False

    def test_different_hashes_for_same_password(self):
        """Test that same password produces different hashes (salt)."""
        password = "TestPassword123!"
        hash1 = get_password_hash(password)
        hash2 = get_password_hash(password)
        assert hash1 != hash2
        assert verify_password(password, hash1) is True
        assert verify_password(password, hash2) is True


class TestJWTTokens:
    """Test JWT token functions."""

    def test_create_access_token(self):
        """Test access token creation."""
        data = {"sub": "testuser", "role": "user"}
        token = create_access_token(data)
        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 50

    def test_create_access_token_with_expiry(self):
        """Test access token creation with custom expiry."""
        data = {"sub": "testuser"}
        expires = timedelta(minutes=15)
        token = create_access_token(data, expires_delta=expires)
        assert token is not None

    def test_create_refresh_token(self):
        """Test refresh token creation."""
        data = {"sub": "testuser"}
        token = create_refresh_token(data)
        assert token is not None
        assert isinstance(token, str)

    def test_decode_valid_token(self):
        """Test decoding a valid token."""
        data = {"sub": "testuser", "role": "admin"}
        token = create_access_token(data)
        payload = decode_token(token)
        assert payload is not None
        assert payload["sub"] == "testuser"
        assert payload["role"] == "admin"
        assert "exp" in payload
        assert payload["type"] == "access"

    def test_decode_invalid_token(self):
        """Test decoding an invalid token."""
        invalid_token = "invalid.token.here"
        payload = decode_token(invalid_token)
        assert payload is None

    def test_decode_malformed_token(self):
        """Test decoding a malformed token."""
        malformed_token = "not-a-jwt-token"
        payload = decode_token(malformed_token)
        assert payload is None

    def test_access_token_contains_type(self):
        """Test that access token contains correct type."""
        data = {"sub": "testuser"}
        token = create_access_token(data)
        payload = decode_token(token)
        assert payload["type"] == "access"

    def test_refresh_token_contains_type(self):
        """Test that refresh token contains correct type."""
        data = {"sub": "testuser"}
        token = create_refresh_token(data)
        payload = decode_token(token)
        assert payload["type"] == "refresh"

    def test_token_expiration_in_payload(self):
        """Test that token contains expiration timestamp."""
        data = {"sub": "testuser"}
        token = create_access_token(data)
        payload = decode_token(token)
        assert "exp" in payload
        assert isinstance(payload["exp"], (int, float))
