"""
Integration tests for admin source edge cases to exercise uncovered branches
in `app/routes/admin.py` (empty update payload and non-existent source operations).
"""

import pytest
from httpx import AsyncClient


async def _create_admin_user(client: AsyncClient, mock_db):
    # Create a user record in the mock DB and bypass auth by overriding
    # the `get_current_admin_user` dependency in the app for this test.
    from app.main import app as _app
    from app.models.schemas import User as UserModel
    from app.utils.dependencies import get_current_admin_user

    # Ensure user exists in DB (so other code that queries DB can find it)
    await mock_db.users.insert_one(
        {
            "username": "edge_admin",
            "email": "edge_admin@example.com",
            "hashed_password": "fakehash",
            "role": "admin",
        }
    )

    # Override dependency to return a User instance for admin access
    def _override_admin():
        return UserModel(username="edge_admin", email="edge_admin@example.com")

    _app.dependency_overrides[get_current_admin_user] = _override_admin
    return None


@pytest.mark.asyncio
async def test_update_source_empty_payload_returns_existing(
    client: AsyncClient, mock_db
):
    # Bypass auth via dependency override; no token required
    await _create_admin_user(client, mock_db)

    # Insert source
    await mock_db.sources.insert_one(
        {
            "name": "ExistingSource",
            "url": "https://existing.com/rss",
            "source_type": "rss",
            "ideology": "center",
            "geography": "US",
            "enabled": True,
        }
    )

    # Send empty update (no fields) -> should return existing source without modification
    response = await client.put("/api/admin/sources/ExistingSource", json={})

    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "ExistingSource"


@pytest.mark.asyncio
async def test_nonexistent_source_operations_return_404(client: AsyncClient, mock_db):
    # Bypass auth via dependency override; no token required
    await _create_admin_user(client, mock_db)

    # Ensure source does not exist
    await mock_db.sources.delete_many({"name": "NoSuchSource"})

    # Delete non-existent
    resp_del = await client.delete("/api/admin/sources/NoSuchSource")
    assert resp_del.status_code == 404

    # Enable non-existent
    resp_enable = await client.put("/api/admin/sources/NoSuchSource/enable")
    assert resp_enable.status_code == 404

    # Disable non-existent
    resp_disable = await client.put("/api/admin/sources/NoSuchSource/disable")
    assert resp_disable.status_code == 404

    # Flag non-existent
    resp_flag = await client.put("/api/admin/sources/NoSuchSource/flag?reason=testing")
    assert resp_flag.status_code == 404


@pytest.mark.asyncio
async def test_update_nonexistent_source_returns_404(client: AsyncClient, mock_db):
    # Bypass auth via dependency override; no token required
    await _create_admin_user(client, mock_db)

    # Ensure source does not exist
    await mock_db.sources.delete_many({"name": "NoSuchSourceUpdate"})

    # Attempt to update a non-existent source -> should return 404
    resp = await client.put(
        "/api/admin/sources/NoSuchSourceUpdate", json={"ideology": "left"}
    )
    assert resp.status_code == 404
