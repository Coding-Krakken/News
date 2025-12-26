"""
Integration tests to cover remaining branches in `app/routes/auth.py`.

Targets:
- refresh token missing `sub`
- refresh token where user not found
- update `/me` with empty payload returns current user
- admin endpoints `update_user_role` and `disable_user` when user not found
"""
import pytest
from httpx import AsyncClient


async def _override_admin_dependency(mock_db):
    from app.main import app as _app
    from app.models.schemas import User as UserModel
    from app.utils.dependencies import get_current_admin_user

    # ensure admin exists
    await mock_db.users.insert_one({
        "username": "admin_branch",
        "email": "admin_branch@example.com",
        "hashed_password": "fake",
        "role": "admin"
    })

    def _override_admin():
        return UserModel(username="admin_branch", email="admin_branch@example.com")

    _app.dependency_overrides[get_current_admin_user] = _override_admin


@pytest.mark.asyncio
async def test_refresh_token_missing_sub(monkeypatch, client: AsyncClient, mock_db):
    # decode_token returns refresh type but no sub
    import app.routes.auth as auth_mod
    monkeypatch.setattr(auth_mod, "decode_token", lambda t: {"type": "refresh"})

    resp = await client.post("/api/auth/refresh?refresh_token=dummy")
    assert resp.status_code == 401
    assert "invalid refresh token" in resp.json()["detail"].lower()


@pytest.mark.asyncio
async def test_refresh_token_user_not_found(monkeypatch, client: AsyncClient, mock_db):
    # decode_token returns sub for a user that doesn't exist
    import app.routes.auth as auth_mod
    monkeypatch.setattr(auth_mod, "decode_token", lambda t: {"type": "refresh", "sub": "ghost"})

    resp = await client.post("/api/auth/refresh?refresh_token=ghosttoken")
    assert resp.status_code == 401
    assert "user not found" in resp.json()["detail"].lower()


@pytest.mark.asyncio
async def test_update_me_empty_returns_current_user(client: AsyncClient, mock_db):
    # Register and login
    await client.post("/api/auth/register", json={
        "username": "meuser",
        "email": "meuser@example.com",
        "password": "TestPass123!"
    })

    login = await client.post(
        "/api/auth/login",
        data={"username": "meuser", "password": "TestPass123!"},
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    token = login.json()["access_token"]

    # Send empty update payload
    resp = await client.put(
        "/api/auth/me",
        json={},
        headers={"Authorization": f"Bearer {token}"}
    )

    assert resp.status_code == 200
    data = resp.json()
    assert data["username"] == "meuser"
    assert data["email"] == "meuser@example.com"


@pytest.mark.asyncio
async def test_update_user_role_nonexistent_returns_404(client: AsyncClient, mock_db):
    await _override_admin_dependency(mock_db)

    resp = await client.put("/api/auth/users/no_such_user/role?role=admin")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_disable_user_nonexistent_returns_404(client: AsyncClient, mock_db):
    await _override_admin_dependency(mock_db)

    resp = await client.put("/api/auth/users/no_such_user/disable")
    assert resp.status_code == 404
