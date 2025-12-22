"""
Integration tests for admin dashboard API endpoints.
"""
import pytest
from httpx import AsyncClient


async def _create_admin_user(client: AsyncClient, mock_db):
    """Helper to create and login an admin user."""
    # Register admin user
    await client.post("/api/auth/register", json={
        "username": "admin",
        "email": "admin@example.com",
        "password": "AdminPass123!"
    })
    
    # Set admin role
    await mock_db.users.update_one(
        {"username": "admin"},
        {"$set": {"role": "admin"}}
    )
    
    # Login
    login_response = await client.post(
        "/api/auth/login",
        data={"username": "admin", "password": "AdminPass123!"},
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    
    return login_response.json()["access_token"]


@pytest.mark.asyncio
class TestAdminSourceManagement:
    """Test admin source management endpoints."""
    
    async def test_list_sources(self, client: AsyncClient, mock_db):
        """Test listing sources as admin."""
        token = await _create_admin_user(client, mock_db)
        
        # Add a test source
        await mock_db.sources.insert_one({
            "name": "Test Source",
            "url": "https://test.com/rss",
            "source_type": "rss",
            "ideology": "center",
            "geography": "United States",
            "enabled": True
        })
        
        # List sources
        response = await client.get(
            "/api/admin/sources",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        sources = response.json()
        assert len(sources) >= 1
        assert any(s["name"] == "Test Source" for s in sources)
    
    async def test_list_sources_unauthorized(self, client: AsyncClient, mock_db):
        """Test listing sources without admin role."""
        # Register regular user
        await client.post("/api/auth/register", json={
            "username": "user",
            "email": "user@example.com",
            "password": "UserPass123!"
        })
        
        # Login as regular user
        login_response = await client.post(
            "/api/auth/login",
            data={"username": "user", "password": "UserPass123!"},
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        token = login_response.json()["access_token"]
        
        # Try to list sources
        response = await client.get(
            "/api/admin/sources",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 403
    
    async def test_create_source(self, client: AsyncClient, mock_db):
        """Test creating a new source."""
        token = await _create_admin_user(client, mock_db)
        
        source_data = {
            "name": "New Source",
            "url": "https://newsource.com/feed",
            "source_type": "rss",
            "ideology": "center-left",
            "geography": "United Kingdom"
        }
        
        response = await client.post(
            "/api/admin/sources",
            json=source_data,
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "New Source"
        assert data["enabled"] is True
        assert data["created_by"] == "admin"
    
    async def test_create_duplicate_source(self, client: AsyncClient, mock_db):
        """Test creating a source with duplicate name."""
        token = await _create_admin_user(client, mock_db)
        
        source_data = {
            "name": "Duplicate Source",
            "url": "https://dup.com/feed"
        }
        
        # Create first source
        await client.post(
            "/api/admin/sources",
            json=source_data,
            headers={"Authorization": f"Bearer {token}"}
        )
        
        # Try to create duplicate
        response = await client.post(
            "/api/admin/sources",
            json=source_data,
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 400
        assert "already exists" in response.json()["detail"].lower()
    
    async def test_get_source(self, client: AsyncClient, mock_db):
        """Test getting a specific source."""
        token = await _create_admin_user(client, mock_db)
        
        # Create source
        await mock_db.sources.insert_one({
            "name": "Test Source",
            "url": "https://test.com/rss",
            "source_type": "rss",
            "ideology": "center",
            "geography": "United States",
            "enabled": True
        })
        
        # Get source
        response = await client.get(
            "/api/admin/sources/Test Source",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Test Source"
    
    async def test_get_nonexistent_source(self, client: AsyncClient, mock_db):
        """Test getting a nonexistent source."""
        token = await _create_admin_user(client, mock_db)
        
        response = await client.get(
            "/api/admin/sources/Nonexistent",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 404
    
    async def test_update_source(self, client: AsyncClient, mock_db):
        """Test updating a source."""
        token = await _create_admin_user(client, mock_db)
        
        # Create source
        await mock_db.sources.insert_one({
            "name": "Test Source",
            "url": "https://test.com/rss",
            "source_type": "rss",
            "ideology": "center",
            "geography": "United States",
            "enabled": True
        })
        
        # Update source
        update_data = {
            "ideology": "center-right",
            "moderation_notes": "Updated ideology"
        }
        
        response = await client.put(
            "/api/admin/sources/Test Source",
            json=update_data,
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["ideology"] == "center-right"
        assert data["moderation_notes"] == "Updated ideology"
    
    async def test_delete_source(self, client: AsyncClient, mock_db):
        """Test deleting a source."""
        token = await _create_admin_user(client, mock_db)
        
        # Create source
        await mock_db.sources.insert_one({
            "name": "Delete Me",
            "url": "https://delete.com/rss",
            "source_type": "rss",
            "ideology": "center",
            "geography": "United States",
            "enabled": True
        })
        
        # Delete source
        response = await client.delete(
            "/api/admin/sources/Delete Me",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        assert "deleted" in response.json()["message"].lower()
        
        # Verify deletion
        source = await mock_db.sources.find_one({"name": "Delete Me"})
        assert source is None
    
    async def test_enable_source(self, client: AsyncClient, mock_db):
        """Test enabling a source."""
        token = await _create_admin_user(client, mock_db)
        
        # Create disabled source
        await mock_db.sources.insert_one({
            "name": "Disabled Source",
            "url": "https://disabled.com/rss",
            "source_type": "rss",
            "ideology": "center",
            "geography": "United States",
            "enabled": False
        })
        
        # Enable source
        response = await client.put(
            "/api/admin/sources/Disabled Source/enable",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        assert "enabled" in response.json()["message"].lower()
    
    async def test_disable_source(self, client: AsyncClient, mock_db):
        """Test disabling a source."""
        token = await _create_admin_user(client, mock_db)
        
        # Create enabled source
        await mock_db.sources.insert_one({
            "name": "Enabled Source",
            "url": "https://enabled.com/rss",
            "source_type": "rss",
            "ideology": "center",
            "geography": "United States",
            "enabled": True
        })
        
        # Disable source
        response = await client.put(
            "/api/admin/sources/Enabled Source/disable",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        assert "disabled" in response.json()["message"].lower()
    
    async def test_flag_source(self, client: AsyncClient, mock_db):
        """Test flagging a source."""
        token = await _create_admin_user(client, mock_db)
        
        # Create source
        await mock_db.sources.insert_one({
            "name": "Flag Me",
            "url": "https://flag.com/rss",
            "source_type": "rss",
            "ideology": "center",
            "geography": "United States",
            "enabled": True
        })
        
        # Flag source
        response = await client.put(
            "/api/admin/sources/Flag Me/flag?reason=Suspicious+content",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        assert "flagged" in response.json()["message"].lower()


@pytest.mark.asyncio
class TestAdminAuditLog:
    """Test admin audit log endpoints."""
    
    async def test_get_audit_log(self, client: AsyncClient, mock_db):
        """Test getting audit log."""
        token = await _create_admin_user(client, mock_db)
        
        # Create some audit log entries
        from datetime import datetime
        await mock_db.audit_log.insert_many([
            {
                "action": "create",
                "entity_type": "source",
                "entity_id": "Test Source",
                "user": "admin",
                "timestamp": datetime.utcnow(),
                "details": {}
            },
            {
                "action": "update",
                "entity_type": "source",
                "entity_id": "Test Source",
                "user": "admin",
                "timestamp": datetime.utcnow(),
                "details": {}
            }
        ])
        
        # Get audit log
        response = await client.get(
            "/api/admin/audit-log",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        logs = response.json()
        assert len(logs) >= 2
    
    async def test_get_audit_log_filtered_by_type(self, client: AsyncClient, mock_db):
        """Test getting audit log filtered by entity type."""
        token = await _create_admin_user(client, mock_db)
        
        from datetime import datetime
        await mock_db.audit_log.insert_many([
            {
                "action": "create",
                "entity_type": "source",
                "entity_id": "Source1",
                "user": "admin",
                "timestamp": datetime.utcnow(),
                "details": {}
            },
            {
                "action": "create",
                "entity_type": "user",
                "entity_id": "user1",
                "user": "admin",
                "timestamp": datetime.utcnow(),
                "details": {}
            }
        ])
        
        # Get audit log filtered by source
        response = await client.get(
            "/api/admin/audit-log?entity_type=source",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        logs = response.json()
        assert all(log["entity_type"] == "source" for log in logs)


@pytest.mark.asyncio
class TestAdminDashboardStats:
    """Test admin dashboard statistics endpoint."""
    
    async def test_get_admin_stats(self, client: AsyncClient, mock_db):
        """Test getting admin dashboard stats."""
        token = await _create_admin_user(client, mock_db)
        
        # Add some test data
        await mock_db.sources.insert_many([
            {"name": "Source1", "url": "https://s1.com", "enabled": True},
            {"name": "Source2", "url": "https://s2.com", "enabled": False}
        ])
        
        # Get stats
        response = await client.get(
            "/api/admin/stats",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        stats = response.json()
        
        assert "users" in stats
        assert "sources" in stats
        assert "content" in stats
        
        assert stats["users"]["total"] >= 1  # At least the admin
        assert stats["sources"]["total"] >= 2
        assert stats["sources"]["enabled"] >= 1
        assert stats["sources"]["disabled"] >= 1
    
    async def test_get_admin_stats_unauthorized(self, client: AsyncClient, mock_db):
        """Test getting stats as regular user (should fail)."""
        # Register regular user
        await client.post("/api/auth/register", json={
            "username": "user",
            "email": "user@example.com",
            "password": "UserPass123!"
        })
        
        # Login
        login_response = await client.post(
            "/api/auth/login",
            data={"username": "user", "password": "UserPass123!"},
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        token = login_response.json()["access_token"]
        
        # Try to get stats
        response = await client.get(
            "/api/admin/stats",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 403
