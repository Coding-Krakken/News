"""
Integration tests for articles API endpoints.
"""
import pytest
from httpx import AsyncClient


@pytest.mark.integration
class TestArticlesAPI:
    """Integration tests for articles endpoints."""
    
    @pytest.mark.asyncio
    async def test_get_articles_empty(self, client: AsyncClient, mock_db):
        """Test getting articles when database is empty."""
        response = await client.get("/api/articles/")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 0
    
    @pytest.mark.asyncio
    async def test_get_sources_list(self, client: AsyncClient):
        """Test getting list of configured sources."""
        response = await client.get("/api/articles/sources/list")
        assert response.status_code == 200
        sources = response.json()
        assert isinstance(sources, list)
        # There should be at least the 4 default sources
        default_names = {"BBC News", "CNN", "Reuters", "The Guardian"}
        found_names = {s["name"] for s in sources}
        assert default_names.issubset(found_names)
        assert all("name" in s for s in sources)
    
    @pytest.mark.asyncio
    async def test_add_source(self, client: AsyncClient):
        """Test adding a new source."""
        response = await client.post(
            "/api/articles/sources/add",
            params={
                "name": "Test Source",
                "url": "https://test.com/rss",
                "source_type": "rss",
                "ideology": "center",
                "geography": "Test Country"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "Test Source" in data["message"]
    
    @pytest.mark.asyncio
    async def test_get_articles_with_pagination(self, client: AsyncClient, mock_db, sample_articles_list):
        """Test getting articles with pagination."""
        # Insert test articles
        for article_data in sample_articles_list:
            await mock_db.articles.insert_one(article_data)
        
        response = await client.get("/api/articles/?skip=0&limit=2")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) <= 2
    
    @pytest.mark.asyncio
    async def test_get_articles_filter_by_source(self, client: AsyncClient, mock_db, sample_articles_list):
        """Test filtering articles by source."""
        # Insert test articles
        for article_data in sample_articles_list:
            await mock_db.articles.insert_one(article_data)
        
        response = await client.get("/api/articles/?source=Source 0")
        
        assert response.status_code == 200
        data = response.json()
        assert all(a["source_name"] == "Source 0" for a in data)
    
    @pytest.mark.asyncio
    async def test_get_articles_filter_by_category(self, client: AsyncClient, mock_db, sample_article_data):
        """Test filtering articles by category."""
        # Insert article with specific category
        sample_article_data["category"] = "technology"
        await mock_db.articles.insert_one(sample_article_data)
        
        response = await client.get("/api/articles/?category=technology")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) > 0
        assert all(a["category"] == "technology" for a in data)
