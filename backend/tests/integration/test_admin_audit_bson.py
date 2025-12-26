"""
Integration test to ensure audit log BSON types are serialized
correctly by the admin audit-log endpoint.
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
            "username": "admin_bson",
            "email": "admin_bson@example.com",
            "hashed_password": "fakehash",
            "role": "admin",
        }
    )

    # Override dependency to return a User instance for admin access
    def _override_admin():
        return UserModel(username="admin_bson", email="admin_bson@example.com")

    # Only override the admin dependency; keep other overrides (like DB)
    _app.dependency_overrides[get_current_admin_user] = _override_admin
    return None


@pytest.mark.asyncio
async def test_audit_log_serializes_objectid(client: AsyncClient, mock_db):
    """Insert audit log entries containing ObjectId and nested structures
    and assert the `/api/admin/audit-log` endpoint returns stringified ids.
    """
    # Bypass auth by overriding dependency; no token needed
    await _create_admin_user(client, mock_db)

    from datetime import datetime
    from bson import ObjectId

    oid = ObjectId()

    await mock_db.audit_log.insert_one(
        {
            "action": "create",
            "entity_type": "source",
            "entity_id": "SourceWithOID",
            "user": "admin_bson",
            "timestamp": datetime.utcnow(),
            "details": {
                "ref": oid,
                "nested": {"list": [oid, {"inner": oid}], "dict": {"sub": oid}},
            },
        }
    )

    # Call without Authorization header because dependency is overridden
    response = await client.get("/api/admin/audit-log")

    assert response.status_code == 200
    logs = response.json()
    # Find our inserted log
    matching = [l for l in logs if l.get("entity_id") == "SourceWithOID"]
    assert matching, "Inserted audit log not returned"
    details = matching[0]["details"]
    # The ObjectId values should have been converted to their string form
    assert details["ref"] == str(oid)
    assert details["nested"]["list"][0] == str(oid)
    assert details["nested"]["list"][1]["inner"] == str(oid)
    assert details["nested"]["dict"]["sub"] == str(oid)


@pytest.mark.asyncio
async def test_audit_log_filter_by_user(client: AsyncClient, mock_db):
    # Bypass auth by overriding dependency; no token needed
    await _create_admin_user(client, mock_db)

    from datetime import datetime
    from bson import ObjectId

    oid = ObjectId()

    await mock_db.audit_log.insert_one(
        {
            "action": "create",
            "entity_type": "source",
            "entity_id": "SourceFilterUser",
            "user": "admin_bson",
            "timestamp": datetime.utcnow(),
            "details": {"ref": oid},
        }
    )

    # Call with user filter
    response = await client.get("/api/admin/audit-log?user=admin_bson")
    assert response.status_code == 200
    logs = response.json()
    assert any(l.get("entity_id") == "SourceFilterUser" for l in logs)
