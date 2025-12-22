"""
Integration tests for authentication API endpoints.
"""
import pytest
from httpx import AsyncClient
from app.models.schemas import UserRole


@pytest.mark.asyncio
class TestAuthRegistration:
    """Test user registration endpoint."""
    
    async def test_register_success(self, client: AsyncClient, mock_db):
        """Test successful user registration."""
        user_data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "TestPass123!",
            "full_name": "Test User"
        }
        
        response = await client.post("/api/auth/register", json=user_data)
        assert response.status_code == 201
        
        data = response.json()
        assert data["username"] == "testuser"
        assert data["email"] == "test@example.com"
        assert data["full_name"] == "Test User"
        assert data["role"] == "user"
        assert "hashed_password" not in data
        assert "password" not in data
    
    async def test_register_duplicate_username(self, client: AsyncClient, mock_db):
        """Test registration with duplicate username."""
        user_data = {
            "username": "testuser",
            "email": "test1@example.com",
            "password": "TestPass123!"
        }
        
        # First registration
        await client.post("/api/auth/register", json=user_data)
        
        # Second registration with same username
        user_data["email"] = "test2@example.com"
        response = await client.post("/api/auth/register", json=user_data)
        
        assert response.status_code == 400
        assert "already registered" in response.json()["detail"].lower()
    
    async def test_register_duplicate_email(self, client: AsyncClient, mock_db):
        """Test registration with duplicate email."""
        user_data = {
            "username": "testuser1",
            "email": "test@example.com",
            "password": "TestPass123!"
        }
        
        # First registration
        await client.post("/api/auth/register", json=user_data)
        
        # Second registration with same email
        user_data["username"] = "testuser2"
        response = await client.post("/api/auth/register", json=user_data)
        
        assert response.status_code == 400
        assert "already registered" in response.json()["detail"].lower()
    
    async def test_register_weak_password(self, client: AsyncClient, mock_db):
        """Test registration with weak password."""
        user_data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "weak"
        }
        
        response = await client.post("/api/auth/register", json=user_data)
        assert response.status_code == 422
    
    async def test_register_invalid_username(self, client: AsyncClient, mock_db):
        """Test registration with invalid username."""
        user_data = {
            "username": "ab",  # Too short
            "email": "test@example.com",
            "password": "TestPass123!"
        }
        
        response = await client.post("/api/auth/register", json=user_data)
        assert response.status_code == 422
    
    async def test_register_invalid_email(self, client: AsyncClient, mock_db):
        """Test registration with invalid email."""
        user_data = {
            "username": "testuser",
            "email": "invalid-email",
            "password": "TestPass123!"
        }
        
        response = await client.post("/api/auth/register", json=user_data)
        assert response.status_code == 422


@pytest.mark.asyncio
class TestAuthLogin:
    """Test login endpoint."""
    
    async def test_login_success(self, client: AsyncClient, mock_db):
        """Test successful login."""
        # Register user first
        user_data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "TestPass123!"
        }
        await client.post("/api/auth/register", json=user_data)
        
        # Login
        login_data = {
            "username": "testuser",
            "password": "TestPass123!"
        }
        response = await client.post(
            "/api/auth/login",
            data=login_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"
    
    async def test_login_wrong_password(self, client: AsyncClient, mock_db):
        """Test login with wrong password."""
        # Register user first
        user_data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "TestPass123!"
        }
        await client.post("/api/auth/register", json=user_data)
        
        # Login with wrong password
        login_data = {
            "username": "testuser",
            "password": "WrongPass123!"
        }
        response = await client.post(
            "/api/auth/login",
            data=login_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        assert response.status_code == 401
        assert "incorrect" in response.json()["detail"].lower()
    
    async def test_login_nonexistent_user(self, client: AsyncClient, mock_db):
        """Test login with nonexistent user."""
        login_data = {
            "username": "nonexistent",
            "password": "TestPass123!"
        }
        response = await client.post(
            "/api/auth/login",
            data=login_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        assert response.status_code == 401


@pytest.mark.asyncio
class TestAuthProfile:
    """Test profile management endpoints."""
    
    async def test_get_profile(self, client: AsyncClient, mock_db):
        """Test getting current user profile."""
        # Register and login
        user_data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "TestPass123!"
        }
        await client.post("/api/auth/register", json=user_data)
        
        login_response = await client.post(
            "/api/auth/login",
            data={"username": "testuser", "password": "TestPass123!"},
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        token = login_response.json()["access_token"]
        
        # Get profile
        response = await client.get(
            "/api/auth/me",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == "testuser"
        assert data["email"] == "test@example.com"
        assert "hashed_password" not in data
    
    async def test_get_profile_unauthorized(self, client: AsyncClient, mock_db):
        """Test getting profile without authentication."""
        response = await client.get("/api/auth/me")
        assert response.status_code == 401
    
    async def test_update_profile(self, client: AsyncClient, mock_db):
        """Test updating user profile."""
        # Register and login
        user_data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "TestPass123!"
        }
        await client.post("/api/auth/register", json=user_data)
        
        login_response = await client.post(
            "/api/auth/login",
            data={"username": "testuser", "password": "TestPass123!"},
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        token = login_response.json()["access_token"]
        
        # Update profile
        update_data = {
            "full_name": "Updated Name",
            "email": "updated@example.com"
        }
        response = await client.put(
            "/api/auth/me",
            json=update_data,
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["full_name"] == "Updated Name"
        assert data["email"] == "updated@example.com"
    
    async def test_update_profile_duplicate_email(self, client: AsyncClient, mock_db):
        """Test updating profile with email already in use."""
        # Register two users
        await client.post("/api/auth/register", json={
            "username": "user1",
            "email": "user1@example.com",
            "password": "TestPass123!"
        })
        await client.post("/api/auth/register", json={
            "username": "user2",
            "email": "user2@example.com",
            "password": "TestPass123!"
        })
        
        # Login as user2
        login_response = await client.post(
            "/api/auth/login",
            data={"username": "user2", "password": "TestPass123!"},
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        token = login_response.json()["access_token"]
        
        # Try to update to user1's email
        response = await client.put(
            "/api/auth/me",
            json={"email": "user1@example.com"},
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 400


@pytest.mark.asyncio
class TestAuthBookmarks:
    """Test bookmark functionality."""
    
    async def test_bookmark_story(self, client: AsyncClient, mock_db):
        """Test bookmarking a story."""
        # Register and login
        await client.post("/api/auth/register", json={
            "username": "testuser",
            "email": "test@example.com",
            "password": "TestPass123!"
        })
        
        login_response = await client.post(
            "/api/auth/login",
            data={"username": "testuser", "password": "TestPass123!"},
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        token = login_response.json()["access_token"]
        
        # Bookmark story
        response = await client.post(
            "/api/auth/me/bookmarks/stories/story123",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        assert "bookmarked" in response.json()["message"].lower()
    
    async def test_get_bookmarks(self, client: AsyncClient, mock_db):
        """Test getting bookmarked stories."""
        # Register and login
        await client.post("/api/auth/register", json={
            "username": "testuser",
            "email": "test@example.com",
            "password": "TestPass123!"
        })
        
        login_response = await client.post(
            "/api/auth/login",
            data={"username": "testuser", "password": "TestPass123!"},
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        token = login_response.json()["access_token"]
        
        # Bookmark stories
        await client.post(
            "/api/auth/me/bookmarks/stories/story1",
            headers={"Authorization": f"Bearer {token}"}
        )
        await client.post(
            "/api/auth/me/bookmarks/stories/story2",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        # Get bookmarks
        response = await client.get(
            "/api/auth/me/bookmarks/stories",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        bookmarks = response.json()
        assert "story1" in bookmarks
        assert "story2" in bookmarks
    
    async def test_remove_bookmark(self, client: AsyncClient, mock_db):
        """Test removing a bookmark."""
        # Register and login
        await client.post("/api/auth/register", json={
            "username": "testuser",
            "email": "test@example.com",
            "password": "TestPass123!"
        })
        
        login_response = await client.post(
            "/api/auth/login",
            data={"username": "testuser", "password": "TestPass123!"},
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        token = login_response.json()["access_token"]
        
        # Bookmark and then remove
        await client.post(
            "/api/auth/me/bookmarks/stories/story1",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        response = await client.delete(
            "/api/auth/me/bookmarks/stories/story1",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        assert "removed" in response.json()["message"].lower()


@pytest.mark.asyncio
class TestAuthAdmin:
    """Test admin endpoints."""
    
    async def test_list_users_as_admin(self, client: AsyncClient, mock_db):
        """Test listing users as admin."""
        # Register admin user
        await client.post("/api/auth/register", json={
            "username": "admin",
            "email": "admin@example.com",
            "password": "AdminPass123!"
        })
        
        # Manually set admin role in database
        await mock_db.users.update_one(
            {"username": "admin"},
            {"$set": {"role": "admin"}}
        )
        
        # Login as admin
        login_response = await client.post(
            "/api/auth/login",
            data={"username": "admin", "password": "AdminPass123!"},
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        token = login_response.json()["access_token"]
        
        # List users
        response = await client.get(
            "/api/auth/users",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        users = response.json()
        assert len(users) >= 1
        assert any(u["username"] == "admin" for u in users)
    
    async def test_list_users_as_regular_user(self, client: AsyncClient, mock_db):
        """Test listing users as regular user (should fail)."""
        # Register regular user
        await client.post("/api/auth/register", json={
            "username": "testuser",
            "email": "test@example.com",
            "password": "TestPass123!"
        })
        
        # Login
        login_response = await client.post(
            "/api/auth/login",
            data={"username": "testuser", "password": "TestPass123!"},
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        token = login_response.json()["access_token"]
        
        # Try to list users
        response = await client.get(
            "/api/auth/users",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 403
    
    async def test_update_user_role(self, client: AsyncClient, mock_db):
        """Test updating user role as admin."""
        # Register admin and regular user
        await client.post("/api/auth/register", json={
            "username": "admin",
            "email": "admin@example.com",
            "password": "AdminPass123!"
        })
        await client.post("/api/auth/register", json={
            "username": "testuser",
            "email": "test@example.com",
            "password": "TestPass123!"
        })
        
        # Set admin role
        await mock_db.users.update_one(
            {"username": "admin"},
            {"$set": {"role": "admin"}}
        )
        
        # Login as admin
        login_response = await client.post(
            "/api/auth/login",
            data={"username": "admin", "password": "AdminPass123!"},
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        token = login_response.json()["access_token"]
        
        # Update user role
        response = await client.put(
            "/api/auth/users/testuser/role?role=admin",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        assert "updated" in response.json()["message"].lower()
    
    async def test_disable_user(self, client: AsyncClient, mock_db):
        """Test disabling user as admin."""
        # Register admin and regular user
        await client.post("/api/auth/register", json={
            "username": "admin",
            "email": "admin@example.com",
            "password": "AdminPass123!"
        })
        await client.post("/api/auth/register", json={
            "username": "testuser",
            "email": "test@example.com",
            "password": "TestPass123!"
        })
        
        # Set admin role
        await mock_db.users.update_one(
            {"username": "admin"},
            {"$set": {"role": "admin"}}
        )
        
        # Login as admin
        login_response = await client.post(
            "/api/auth/login",
            data={"username": "admin", "password": "AdminPass123!"},
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        token = login_response.json()["access_token"]
        
        # Disable user
        response = await client.put(
            "/api/auth/users/testuser/disable",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        assert "disabled" in response.json()["message"].lower()


@pytest.mark.asyncio
class TestTokenRefresh:
    """Test token refresh endpoint."""
    
    async def test_refresh_token_success(self, client: AsyncClient, mock_db):
        """Test successful token refresh."""
        # Register and login
        await client.post("/api/auth/register", json={
            "username": "testuser",
            "email": "test@example.com",
            "password": "TestPass123!"
        })
        
        login_response = await client.post(
            "/api/auth/login",
            data={"username": "testuser", "password": "TestPass123!"},
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        refresh_token = login_response.json()["refresh_token"]
        
        # Refresh token
        response = await client.post(
            f"/api/auth/refresh?refresh_token={refresh_token}"
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
    
    async def test_refresh_token_invalid(self, client: AsyncClient, mock_db):
        """Test token refresh with invalid token."""
        response = await client.post(
            "/api/auth/refresh?refresh_token=invalid_token"
        )
        
        assert response.status_code == 401
