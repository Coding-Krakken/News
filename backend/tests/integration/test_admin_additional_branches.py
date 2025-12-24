"""
Integration tests to hit additional admin branches uncovered by coverage.

- list_sources with `enabled_only` True
- create_source when duplicate exists (400)
- update_source with `url` field to trigger URL conversion branch
"""
import pytest
from httpx import AsyncClient


async def _override_admin_dependency(mock_db):
    from app.main import app as _app
    from app.models.schemas import User as UserModel
    from app.utils.dependencies import get_current_admin_user

    # ensure admin user exists in mock DB
    await mock_db.users.insert_one({
        "username": "branch_admin",
        "email": "branch_admin@example.com",
        "hashed_password": "fake",
        "role": "admin",
    })

    def _override_admin():
        return UserModel(username="branch_admin", email="branch_admin@example.com")

    _app.dependency_overrides[get_current_admin_user] = _override_admin


@pytest.mark.asyncio
async def test_list_sources_enabled_only(client: AsyncClient, mock_db):
    await _override_admin_dependency(mock_db)

    # insert enabled and disabled sources
    await mock_db.sources.insert_many([
        {"name": "Enabled1", "url": "https://e1.com/rss", "enabled": True},
        {"name": "Disabled1", "url": "https://d1.com/rss", "enabled": False}
    ])

    resp = await client.get("/api/admin/sources?enabled_only=true")
    assert resp.status_code == 200
    data = resp.json()
    names = [s["name"] for s in data]
    assert "Enabled1" in names
    assert "Disabled1" not in names


@pytest.mark.asyncio
async def test_create_source_duplicate_returns_400(client: AsyncClient, mock_db):
    await _override_admin_dependency(mock_db)

    # existing source
    await mock_db.sources.insert_one({
        "name": "DupSource",
        "url": "https://dup.com/rss",
        "source_type": "rss",
        "ideology": "center",
        "geography": "US",
        "enabled": True
    })

    payload = {
        "name": "DupSource",
        "url": "https://dup.com/rss",
        "source_type": "rss",
        "ideology": "center",
        "geography": "US"
    }

    resp = await client.post("/api/admin/sources", json=payload)
    assert resp.status_code == 400


@pytest.mark.asyncio
async def test_update_source_converts_url_and_updates(client: AsyncClient, mock_db):
    await _override_admin_dependency(mock_db)

    # insert initial source
    await mock_db.sources.insert_one({
        "name": "ToUpdate",
        "url": "https://old.example.com/rss",
        "source_type": "rss",
        "ideology": "center",
        "geography": "US",
        "enabled": True
    })

    # Update with a new URL (string) - should be converted/stored as string
    resp = await client.put("/api/admin/sources/ToUpdate", json={"url": "https://new.example.com/rss"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["url"] == "https://new.example.com/rss"
