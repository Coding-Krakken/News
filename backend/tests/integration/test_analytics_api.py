"""
Integration tests for analytics API endpoints.
"""

import pytest
from httpx import AsyncClient


@pytest.mark.integration
class TestAnalyticsAPI:
    """Integration tests for analytics endpoints."""

    @pytest.mark.asyncio
    async def test_get_stats_empty(self, client: AsyncClient, mock_db):
        """Test getting stats when database is empty."""
        response = await client.get("/api/analytics/stats")

        assert response.status_code == 200
        data = response.json()
        assert data["total_articles"] == 0
        assert data["total_stories"] == 0

    @pytest.mark.asyncio
    async def test_get_stats_with_data(
        self, client: AsyncClient, mock_db, sample_articles_list, sample_story_data
    ):
        """Test getting stats with data in database."""
        # Insert articles
        for article_data in sample_articles_list:
            await mock_db.articles.insert_one(article_data)

        # Insert story
        await mock_db.stories.insert_one(sample_story_data)

        response = await client.get("/api/analytics/stats")

        assert response.status_code == 200
        data = response.json()
        assert data["total_articles"] == len(sample_articles_list)
        assert data["total_stories"] == 1
        assert "by_source" in data
        assert "by_category" in data

    @pytest.mark.asyncio
    async def test_get_facets_empty(self, client: AsyncClient, mock_db):
        """Test getting facets when database is empty."""
        response = await client.get("/api/analytics/facets")

        assert response.status_code == 200
        data = response.json()
        assert "sources" in data
        assert "categories" in data
        assert "geographies" in data
        assert "ideologies" in data

    @pytest.mark.asyncio
    async def test_get_facets_with_data(
        self, client: AsyncClient, mock_db, sample_articles_list
    ):
        """Test getting facets with data."""
        # Insert articles with specific attributes
        for i, article_data in enumerate(sample_articles_list):
            article_data["category"] = f"category_{i % 2}"
            article_data["geography"] = f"geo_{i % 2}"
            article_data["ideology"] = "center"
            await mock_db.articles.insert_one(article_data)

        response = await client.get("/api/analytics/facets")

        assert response.status_code == 200
        data = response.json()
        assert len(data["sources"]) > 0
        assert len(data["categories"]) > 0
        assert "center" in data["ideologies"]

    @pytest.mark.asyncio
    async def test_filter_articles_by_sources(
        self, client: AsyncClient, mock_db, sample_articles_list
    ):
        """Test filtering articles by sources."""
        # Insert articles
        for article_data in sample_articles_list:
            await mock_db.articles.insert_one(article_data)

        response = await client.get("/api/analytics/filter?sources=Source 0")

        assert response.status_code == 200
        data = response.json()
        assert all(a["source_name"] == "Source 0" for a in data)

    @pytest.mark.asyncio
    async def test_filter_articles_by_categories(
        self, client: AsyncClient, mock_db, sample_articles_list
    ):
        """Test filtering articles by categories."""
        # Insert articles with categories
        for i, article_data in enumerate(sample_articles_list):
            article_data["category"] = "tech" if i < 2 else "politics"
            await mock_db.articles.insert_one(article_data)

        response = await client.get("/api/analytics/filter?categories=tech")

        assert response.status_code == 200
        data = response.json()
        assert all(a["category"] == "tech" for a in data)

    @pytest.mark.asyncio
    async def test_filter_articles_by_geographies(
        self, client: AsyncClient, mock_db, sample_articles_list
    ):
        """Test filtering articles by geographies."""
        # Insert articles with geographies
        for i, article_data in enumerate(sample_articles_list):
            article_data["geography"] = "US" if i < 2 else "UK"
            await mock_db.articles.insert_one(article_data)

        response = await client.get("/api/analytics/filter?geographies=US")

        assert response.status_code == 200
        data = response.json()
        assert all(a["geography"] == "US" for a in data)

    @pytest.mark.asyncio
    async def test_filter_articles_by_ideologies(
        self, client: AsyncClient, mock_db, sample_articles_list
    ):
        """Test filtering articles by ideologies."""
        # Insert articles with ideologies
        for i, article_data in enumerate(sample_articles_list):
            article_data["ideology"] = "left" if i < 2 else "right"
            await mock_db.articles.insert_one(article_data)

        response = await client.get("/api/analytics/filter?ideologies=left")

        assert response.status_code == 200
        data = response.json()
        assert all(a["ideology"] == "left" for a in data)

    @pytest.mark.asyncio
    async def test_filter_articles_multiple_criteria(
        self, client: AsyncClient, mock_db, sample_articles_list
    ):
        """Test filtering by multiple criteria."""
        # Insert articles
        for i, article_data in enumerate(sample_articles_list):
            article_data["category"] = "tech"
            article_data["geography"] = "US" if i < 2 else "UK"
            await mock_db.articles.insert_one(article_data)

        response = await client.get(
            "/api/analytics/filter?categories=tech&geographies=US"
        )

        assert response.status_code == 200
        data = response.json()
        assert all(a["category"] == "tech" and a["geography"] == "US" for a in data)

    @pytest.mark.asyncio
    async def test_filter_articles_with_pagination(
        self, client: AsyncClient, mock_db, sample_articles_list
    ):
        """Test filtering with pagination."""
        # Insert articles
        for article_data in sample_articles_list:
            await mock_db.articles.insert_one(article_data)

        response = await client.get("/api/analytics/filter?skip=0&limit=2")

        assert response.status_code == 200
        data = response.json()
        assert len(data) <= 2
