import pytest
import importlib

from fastapi import HTTPException


@pytest.mark.asyncio
async def test_get_current_user_invalid_token(monkeypatch):
    # Simulate decode_token returning None
    deps = importlib.import_module("app.utils.dependencies")

    monkeypatch.setattr(deps, "decode_token", lambda token: None)

    with pytest.raises(HTTPException):
        await deps.get_current_user(token="some.invalid.token")


@pytest.mark.asyncio
async def test_get_current_user_missing_sub(monkeypatch):
    deps = importlib.import_module("app.utils.dependencies")

    monkeypatch.setattr(deps, "decode_token", lambda token: {})

    with pytest.raises(HTTPException):
        await deps.get_current_user(token="token-without-sub")


@pytest.mark.asyncio
async def test_get_current_user_user_not_found(monkeypatch):
    deps = importlib.import_module("app.utils.dependencies")

    monkeypatch.setattr(deps, "decode_token", lambda token: {"sub": "nouser"})

    class DummyDB:
        class users:
            @staticmethod
            async def find_one(query):
                return None

    monkeypatch.setattr(deps, "get_database", lambda: DummyDB())

    with pytest.raises(HTTPException):
        await deps.get_current_user(token="token")


@pytest.mark.asyncio
async def test_get_current_user_success(monkeypatch):
    deps = importlib.import_module("app.utils.dependencies")

    monkeypatch.setattr(deps, "decode_token", lambda token: {"sub": "alice"})

    user_record = {
        "username": "alice",
        "email": "a@b.com",
        "hashed_password": "x",
        "role": "user",
        "disabled": False,
    }

    class DummyDB:
        class users:
            @staticmethod
            async def find_one(query):
                return user_record.copy()

    monkeypatch.setattr(deps, "get_database", lambda: DummyDB())

    user = await deps.get_current_user(token="goodtoken")
    assert user.username == "alice"


@pytest.mark.asyncio
async def test_get_optional_user_none_and_invalid(monkeypatch):
    deps = importlib.import_module("app.utils.dependencies")

    # token None -> returns None
    res = await deps.get_optional_user(token=None)
    assert res is None

    # invalid token -> should return None (catch HTTPException)
    monkeypatch.setattr(
        deps,
        "get_current_user",
        lambda token: (_ for _ in ()).throw(HTTPException(status_code=401)),
    )
    res = await deps.get_optional_user(token="bad")
    assert res is None


def test_get_current_active_user_raises_for_disabled():
    deps = importlib.import_module("app.utils.dependencies")

    class DummyUser:
        disabled = True

    with pytest.raises(HTTPException):
        # call sync function (not awaited) because it raises immediately
        import asyncio

        asyncio.get_event_loop().run_until_complete(
            deps.get_current_active_user(current_user=DummyUser())
        )


def test_get_current_admin_user_forbidden():
    deps = importlib.import_module("app.utils.dependencies")

    class DummyUser:
        disabled = False
        role = "user"

    with pytest.raises(HTTPException):
        import asyncio

        asyncio.get_event_loop().run_until_complete(
            deps.get_current_admin_user(current_user=DummyUser())
        )
