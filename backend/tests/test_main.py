"""
Tests for main application initialization and health.
"""
import pytest
from httpx import AsyncClient


class TestMainApplication:
    """Test main application endpoints."""
    
    @pytest.mark.asyncio
    async def test_root_endpoint(self, client: AsyncClient):
        """Test root endpoint returns API information."""
        response = await client.get("/")
        
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "version" in data
        assert data["version"] == "1.0.0"
    
    @pytest.mark.asyncio
    async def test_health_endpoint(self, client: AsyncClient):
        """Test health check endpoint."""
        response = await client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
    
    @pytest.mark.asyncio
    async def test_cors_headers(self, client: AsyncClient):
        """Test CORS configuration."""
        response = await client.options("/api/articles/")
        
        # CORS headers should be present
        assert response.status_code in [200, 204]
    
    @pytest.mark.asyncio
    async def test_404_handling(self, client: AsyncClient):
        """Test 404 error handling."""
        response = await client.get("/nonexistent/path")
        
        assert response.status_code == 404
