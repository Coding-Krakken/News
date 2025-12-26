"""
End-to-end tests for authentication and admin workflows.
"""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
class TestAuthAdminE2E:
    """Test complete authentication and admin workflows."""

    async def test_complete_user_journey(self, client: AsyncClient, mock_db):
        """Test complete user registration, login, and profile management flow."""
        # Step 1: Register user
        register_data = {
            "username": "johndoe",
            "email": "john@example.com",
            "password": "SecurePass123!",
            "full_name": "John Doe",
        }

        register_response = await client.post("/api/auth/register", json=register_data)
        assert register_response.status_code == 201
        user_data = register_response.json()
        assert user_data["username"] == "johndoe"
        assert user_data["email"] == "john@example.com"
        assert user_data["role"] == "user"

        # Step 2: Login
        login_response = await client.post(
            "/api/auth/login",
            data={"username": "johndoe", "password": "SecurePass123!"},
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        assert login_response.status_code == 200
        tokens = login_response.json()
        access_token = tokens["access_token"]
        refresh_token = tokens["refresh_token"]

        # Step 3: Get profile
        profile_response = await client.get(
            "/api/auth/me", headers={"Authorization": f"Bearer {access_token}"}
        )
        assert profile_response.status_code == 200
        profile = profile_response.json()
        assert profile["username"] == "johndoe"

        # Step 4: Update profile
        update_response = await client.put(
            "/api/auth/me",
            json={"full_name": "John Updated Doe"},
            headers={"Authorization": f"Bearer {access_token}"},
        )
        assert update_response.status_code == 200
        updated_profile = update_response.json()
        assert updated_profile["full_name"] == "John Updated Doe"

        # Step 5: Bookmark a story
        bookmark_response = await client.post(
            "/api/auth/me/bookmarks/stories/story123",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        assert bookmark_response.status_code == 200

        # Step 6: Get bookmarks
        bookmarks_response = await client.get(
            "/api/auth/me/bookmarks/stories",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        assert bookmarks_response.status_code == 200
        bookmarks = bookmarks_response.json()
        assert "story123" in bookmarks

        # Step 7: Refresh token
        refresh_response = await client.post(
            f"/api/auth/refresh?refresh_token={refresh_token}"
        )
        assert refresh_response.status_code == 200
        new_tokens = refresh_response.json()
        assert "access_token" in new_tokens
        assert "refresh_token" in new_tokens

    async def test_complete_admin_journey(self, client: AsyncClient, mock_db):
        """Test complete admin registration, promotion, and source management flow."""
        # Step 1: Register user
        await client.post(
            "/api/auth/register",
            json={
                "username": "adminuser",
                "email": "admin@example.com",
                "password": "AdminPass123!",
            },
        )

        # Step 2: Promote to admin (simulating manual promotion)
        await mock_db.users.update_one(
            {"username": "adminuser"}, {"$set": {"role": "admin"}}
        )

        # Step 3: Login as admin
        login_response = await client.post(
            "/api/auth/login",
            data={"username": "adminuser", "password": "AdminPass123!"},
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        token = login_response.json()["access_token"]

        # Step 4: Create a news source
        source_data = {
            "name": "Tech News Daily",
            "url": "https://technews.com/rss",
            "source_type": "rss",
            "ideology": "center",
            "geography": "United States",
            "category": "technology",
        }

        create_response = await client.post(
            "/api/admin/sources",
            json=source_data,
            headers={"Authorization": f"Bearer {token}"},
        )
        assert create_response.status_code == 201
        created_source = create_response.json()
        assert created_source["name"] == "Tech News Daily"
        assert created_source["enabled"] is True
        assert created_source["created_by"] == "adminuser"

        # Step 5: List sources
        list_response = await client.get(
            "/api/admin/sources", headers={"Authorization": f"Bearer {token}"}
        )
        assert list_response.status_code == 200
        sources = list_response.json()
        assert any(s["name"] == "Tech News Daily" for s in sources)

        # Step 6: Update source
        update_response = await client.put(
            "/api/admin/sources/Tech News Daily",
            json={"moderation_notes": "Verified and approved"},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert update_response.status_code == 200
        updated_source = update_response.json()
        assert updated_source["moderation_notes"] == "Verified and approved"

        # Step 7: Flag source
        flag_response = await client.put(
            "/api/admin/sources/Tech News Daily/flag?reason=Review+needed",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert flag_response.status_code == 200

        # Step 8: Disable source
        disable_response = await client.put(
            "/api/admin/sources/Tech News Daily/disable",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert disable_response.status_code == 200

        # Step 9: Get audit log
        audit_response = await client.get(
            "/api/admin/audit-log", headers={"Authorization": f"Bearer {token}"}
        )
        assert audit_response.status_code == 200
        audit_logs = audit_response.json()
        assert len(audit_logs) >= 4  # create, update, flag, disable

        # Step 10: Get admin stats
        stats_response = await client.get(
            "/api/admin/stats", headers={"Authorization": f"Bearer {token}"}
        )
        assert stats_response.status_code == 200
        stats = stats_response.json()
        assert stats["users"]["total"] >= 1
        assert stats["sources"]["total"] >= 1

    async def test_rbac_enforcement(self, client: AsyncClient, mock_db):
        """Test role-based access control enforcement."""
        # Create regular user
        await client.post(
            "/api/auth/register",
            json={
                "username": "regularuser",
                "email": "regular@example.com",
                "password": "RegularPass123!",
            },
        )

        # Create admin user
        await client.post(
            "/api/auth/register",
            json={
                "username": "adminuser",
                "email": "admin@example.com",
                "password": "AdminPass123!",
            },
        )
        await mock_db.users.update_one(
            {"username": "adminuser"}, {"$set": {"role": "admin"}}
        )

        # Login both users
        regular_login = await client.post(
            "/api/auth/login",
            data={"username": "regularuser", "password": "RegularPass123!"},
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        regular_token = regular_login.json()["access_token"]

        admin_login = await client.post(
            "/api/auth/login",
            data={"username": "adminuser", "password": "AdminPass123!"},
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        admin_token = admin_login.json()["access_token"]

        # Regular user should NOT access admin endpoints
        regular_sources_response = await client.get(
            "/api/admin/sources", headers={"Authorization": f"Bearer {regular_token}"}
        )
        assert regular_sources_response.status_code == 403

        regular_stats_response = await client.get(
            "/api/admin/stats", headers={"Authorization": f"Bearer {regular_token}"}
        )
        assert regular_stats_response.status_code == 403

        # Admin should access admin endpoints
        admin_sources_response = await client.get(
            "/api/admin/sources", headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert admin_sources_response.status_code == 200

        admin_stats_response = await client.get(
            "/api/admin/stats", headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert admin_stats_response.status_code == 200

        # Both should access their own profile
        regular_profile = await client.get(
            "/api/auth/me", headers={"Authorization": f"Bearer {regular_token}"}
        )
        assert regular_profile.status_code == 200

        admin_profile = await client.get(
            "/api/auth/me", headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert admin_profile.status_code == 200

    async def test_user_management_by_admin(self, client: AsyncClient, mock_db):
        """Test admin managing other users."""
        # Create admin
        await client.post(
            "/api/auth/register",
            json={
                "username": "superadmin",
                "email": "superadmin@example.com",
                "password": "SuperAdmin123!",
            },
        )
        await mock_db.users.update_one(
            {"username": "superadmin"}, {"$set": {"role": "admin"}}
        )

        # Create regular users
        await client.post(
            "/api/auth/register",
            json={
                "username": "user1",
                "email": "user1@example.com",
                "password": "User1Pass123!",
            },
        )
        await client.post(
            "/api/auth/register",
            json={
                "username": "user2",
                "email": "user2@example.com",
                "password": "User2Pass123!",
            },
        )

        # Login as admin
        admin_login = await client.post(
            "/api/auth/login",
            data={"username": "superadmin", "password": "SuperAdmin123!"},
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        admin_token = admin_login.json()["access_token"]

        # List all users
        users_response = await client.get(
            "/api/auth/users", headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert users_response.status_code == 200
        users = users_response.json()
        assert len(users) >= 3  # superadmin, user1, user2

        # Promote user1 to admin
        promote_response = await client.put(
            "/api/auth/users/user1/role?role=admin",
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert promote_response.status_code == 200

        # Disable user2
        disable_response = await client.put(
            "/api/auth/users/user2/disable",
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert disable_response.status_code == 200

        # Verify user2 cannot login
        user2_login = await client.post(
            "/api/auth/login",
            data={"username": "user2", "password": "User2Pass123!"},
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        # User can login but will be rejected when trying to access protected resources
        assert user2_login.status_code == 200
        user2_token = user2_login.json()["access_token"]

        # Try to access profile (should fail because user is disabled)
        profile_response = await client.get(
            "/api/auth/me", headers={"Authorization": f"Bearer {user2_token}"}
        )
        assert profile_response.status_code == 400  # Inactive user
