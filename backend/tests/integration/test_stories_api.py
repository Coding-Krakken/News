"""
Integration tests for stories API endpoints.
"""

import pytest
from httpx import AsyncClient


@pytest.mark.integration
class TestStoriesAPI:
    """Integration tests for stories endpoints."""

    @pytest.mark.asyncio
    async def test_get_stories_empty(self, client: AsyncClient, mock_db):
        """Test getting stories when database is empty."""
        response = await client.get("/api/stories/")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 0

    @pytest.mark.asyncio
    async def test_get_stories_with_data(
        self, client: AsyncClient, mock_db, sample_story_data
    ):
        """Test getting stories from database."""
        # Insert test story
        await mock_db.stories.insert_one(sample_story_data)

        response = await client.get("/api/stories/")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["story_id"] == sample_story_data["story_id"]

    @pytest.mark.asyncio
    async def test_get_story_by_id(
        self, client: AsyncClient, mock_db, sample_story_data
    ):
        """Test getting a specific story by ID."""
        await mock_db.stories.insert_one(sample_story_data)

        response = await client.get(f"/api/stories/{sample_story_data['story_id']}")

        assert response.status_code == 200
        data = response.json()
        assert data["story_id"] == sample_story_data["story_id"]
        assert data["title"] == sample_story_data["title"]

    @pytest.mark.asyncio
    async def test_get_story_not_found(self, client: AsyncClient, mock_db):
        """Test getting a non-existent story."""
        response = await client.get("/api/stories/nonexistent_id")

        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_get_story_articles(
        self, client: AsyncClient, mock_db, sample_story_data, sample_articles_list
    ):
        """Test getting articles for a story."""
        # Insert story
        await mock_db.stories.insert_one(sample_story_data)

        # Insert articles referenced by story
        for i, article_url in enumerate(sample_story_data["article_ids"]):
            article_data = sample_articles_list[i].copy()
            article_data["url"] = article_url
            await mock_db.articles.insert_one(article_data)

        response = await client.get(
            f"/api/stories/{sample_story_data['story_id']}/articles"
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data) == len(sample_story_data["article_ids"])

    @pytest.mark.asyncio
    async def test_get_story_coverage(
        self, client: AsyncClient, mock_db, sample_story_data, sample_articles_list
    ):
        """Test getting coverage matrix for a story."""
        # Insert story
        await mock_db.stories.insert_one(sample_story_data)

        # Insert some articles to create sources
        for article_data in sample_articles_list[:2]:
            await mock_db.articles.insert_one(article_data)

        response = await client.get(
            f"/api/stories/{sample_story_data['story_id']}/coverage"
        )

        assert response.status_code == 200
        data = response.json()
        assert "coverage" in data
        assert "sources_covered" in data
        assert "coverage_percentage" in data
        assert isinstance(data["coverage"], dict)

    @pytest.mark.asyncio
    async def test_cluster_stories_trigger(self, client: AsyncClient, mock_db):
        """Test triggering story clustering."""
        response = await client.post("/api/stories/cluster")

        assert response.status_code == 200
        data = response.json()
        assert "message" in data

    @pytest.mark.asyncio
    async def test_get_stories_pagination(
        self, client: AsyncClient, mock_db, sample_story_data
    ):
        """Test pagination for stories endpoint."""
        # Insert multiple stories
        for i in range(5):
            story = sample_story_data.copy()
            story["story_id"] = f"story_{i}"
            await mock_db.stories.insert_one(story)

        response = await client.get("/api/stories/?skip=0&limit=2")

        assert response.status_code == 200
        data = response.json()
        assert len(data) <= 2
