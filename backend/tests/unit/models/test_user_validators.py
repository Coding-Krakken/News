import pytest
from pydantic import ValidationError

from app.models.schemas import UserCreate


def test_username_non_alphanumeric_raises():
    with pytest.raises(ValidationError):
        UserCreate(username="bad!name", email="a@b.com", password="GoodPass1")


def test_username_too_short_raises():
    with pytest.raises(ValidationError):
        UserCreate(username="ab", email="a@b.com", password="GoodPass1")


def test_password_too_short_raises():
    with pytest.raises(ValidationError):
        UserCreate(username="goodname", email="a@b.com", password="Short1")


def test_password_missing_uppercase_raises():
    with pytest.raises(ValidationError):
        UserCreate(username="goodname", email="a@b.com", password="lowercase1")


def test_password_missing_digit_raises():
    with pytest.raises(ValidationError):
        UserCreate(username="goodname", email="a@b.com", password="NoDigitsHere")


def test_password_missing_lowercase_raises():
    with pytest.raises(ValidationError):
        UserCreate(username="goodname", email="a@b.com", password="UPPERCASE1")
