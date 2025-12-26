"""
Additional integration tests to increase coverage for articles, stories, analytics, and ingestion edge cases.
"""

import pytest
from httpx import AsyncClient
from datetime import datetime, timedelta


@pytest.mark.integration
class TestCoverageEdgeCases:

    @pytest.mark.asyncio
    async def test_get_article_not_found(self, client: AsyncClient):
        resp = await client.get("/api/articles/nonexistent-url")
        assert resp.status_code == 404
        assert resp.json()["detail"] == "Article not found"

    @pytest.mark.asyncio
    async def test_add_source_error(self, client: AsyncClient, monkeypatch):
        from app.routes.articles import ingestion_service

        def broken_add_source(*args, **kwargs):
            raise Exception("add source error")

        monkeypatch.setattr(ingestion_service, "add_source", broken_add_source)
        resp = await client.post(
            "/api/articles/sources/add",
            params={
                "name": "ErrSource",
                "url": "http://err.com/rss",
                "source_type": "rss",
                "ideology": "center",
                "geography": "Test",
            },
        )
        assert resp.status_code == 500
        assert "add source error" in resp.json()["detail"]

    @pytest.mark.asyncio
    async def test_get_story_not_found(self, client: AsyncClient):
        resp = await client.get("/api/stories/doesnotexist")
        assert resp.status_code == 404
        assert resp.json()["detail"] == "Story not found"

    @pytest.mark.asyncio
    async def test_get_story_articles_not_found(self, client: AsyncClient):
        resp = await client.get("/api/stories/doesnotexist/articles")
        assert resp.status_code == 404
        assert resp.json()["detail"] == "Story not found"

    @pytest.mark.asyncio
    async def test_get_story_coverage_not_found(self, client: AsyncClient):
        resp = await client.get("/api/stories/doesnotexist/coverage")
        assert resp.status_code == 404
        assert resp.json()["detail"] == "Story not found"

    @pytest.mark.asyncio
    async def test_generate_fact_ledger_story_not_found(self, client: AsyncClient):
        resp = await client.post("/api/fact-checker/doesnotexist")
        assert resp.status_code == 404
        assert resp.json()["detail"] == "Story not found"

    @pytest.mark.asyncio
    async def test_get_fact_ledger_not_found(self, client: AsyncClient):
        resp = await client.get("/api/fact-checker/doesnotexist")
        assert resp.status_code == 404
        assert "Fact ledger not found" in resp.json()["detail"]

    # Removed incomplete test_get_articles_db_error and stray code
    @pytest.mark.asyncio
    async def test_add_source_duplicate(self, client: AsyncClient):
        # Add a source
        params = {
            "name": "DuplicateSource",
            "url": "http://dupe.com/rss",
            "source_type": "rss",
            "ideology": "center",
            "geography": "Test",
        }
        resp1 = await client.post("/api/articles/sources/add", params=params)
        assert resp1.status_code == 200
        # Add again (should still succeed, as current logic just appends)
        resp2 = await client.post("/api/articles/sources/add", params=params)
        assert resp2.status_code == 200

    @pytest.mark.asyncio
    async def test_ingest_articles_error(self, client: AsyncClient, monkeypatch):
        from app.routes.articles import ingestion_service

        async def fake_ingest_all_sources():
            raise Exception("ingest error")

        monkeypatch.setattr(
            ingestion_service, "ingest_all_sources", fake_ingest_all_sources
        )
        resp = await client.post("/api/articles/ingest")
        assert resp.status_code == 500
        assert "ingest error" in resp.json()["detail"]

    @pytest.mark.asyncio
    async def test_analytics_filter_invalid_date(self, client: AsyncClient):
        # Invalid date format
        resp = await client.get("/api/analytics/filter?start_date=notadate")
        assert resp.status_code == 500

    @pytest.mark.asyncio
    async def test_get_facets_empty(self, client: AsyncClient):
        resp = await client.get("/api/analytics/facets")
        assert resp.status_code == 200
        data = resp.json()
        assert set(data.keys()) == {
            "sources",
            "categories",
            "geographies",
            "ideologies",
        }

    @pytest.mark.asyncio
    async def test_trigger_clustering_background(self, client: AsyncClient):
        resp = await client.post("/api/stories/cluster")
        assert resp.status_code == 200
        assert resp.json()["message"] == "Clustering started in background"

    @pytest.mark.asyncio
    async def test_get_story_not_found(self, client: AsyncClient):
        resp = await client.get("/api/stories/doesnotexist")
        assert resp.status_code == 404
        assert resp.json()["detail"] == "Story not found"

    @pytest.mark.asyncio
    async def test_get_story_articles_not_found_2(self, client: AsyncClient):
        # Should return 404 for missing story
        resp = await client.get("/api/stories/doesnotexist/articles")
        assert resp.status_code == 404

    @pytest.mark.asyncio
    async def test_get_story_coverage_not_found_2(self, client: AsyncClient):
        # Should return 404 for missing story
        resp = await client.get("/api/stories/doesnotexist/coverage")
        assert resp.status_code == 404

    @pytest.mark.asyncio
    async def test_get_article_by_url_not_found(self, client: AsyncClient):
        resp = await client.get("/api/articles/nonexistent-url")
        assert resp.status_code == 404
        assert resp.json()["detail"] == "Article not found"

    @pytest.mark.asyncio
    async def test_get_article_by_url_success(
        self, client: AsyncClient, mock_db, sample_articles_list
    ):
        article = sample_articles_list[0]
        await mock_db.articles.insert_one(article)
        url = article["url"]
        resp = await client.get(f"/api/articles/{url}")
        assert resp.status_code == 200
        data = resp.json()
        assert data["url"] == url

    @pytest.mark.asyncio
    async def test_get_stories_pagination(
        self, client: AsyncClient, mock_db, sample_story_data
    ):
        # Insert multiple stories
        for i in range(5):
            s = dict(sample_story_data)
            s["story_id"] = f"story-{i}"
            await mock_db.stories.insert_one(s)
        resp = await client.get("/api/stories/?skip=2&limit=2")
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, list)
        assert len(data) == 2

    @pytest.mark.asyncio
    async def test_analytics_filter_by_multiple_criteria(
        self, client: AsyncClient, mock_db, sample_articles_list
    ):
        # Insert articles with different sources and categories
        for i, article in enumerate(sample_articles_list[:3]):
            article["source_name"] = f"Source{i}"
            article["category"] = f"Cat{i%2}"
            await mock_db.articles.insert_one(article)
        resp = await client.get(
            "/api/analytics/filter?sources=Source0,Source1&categories=Cat0"
        )
        assert resp.status_code == 200
        data = resp.json()
        assert all(a["source_name"] in ["Source0", "Source1"] for a in data)
        assert all(a["category"] == "Cat0" for a in data)

    @pytest.mark.asyncio
    async def test_get_articles_invalid_limit(self, client: AsyncClient):
        resp = await client.get("/api/articles/?limit=0")
        assert resp.status_code == 422

    @pytest.mark.asyncio
    async def test_get_articles_invalid_skip(self, client: AsyncClient):
        resp = await client.get("/api/articles/?skip=-5")
        assert resp.status_code == 422

    @pytest.mark.asyncio
    async def test_add_source_missing_url(self, client: AsyncClient):
        resp = await client.post(
            "/api/articles/sources/add",
            params={
                "name": "NoURL",
                "source_type": "rss",
                "ideology": "center",
                "geography": "Test",
            },
        )
        assert resp.status_code == 422

    @pytest.mark.asyncio
    async def test_get_story_articles_not_found(self, client: AsyncClient):
        resp = await client.get("/api/stories/doesnotexist/articles")
        assert resp.status_code == 404

    @pytest.mark.asyncio
    async def test_get_story_coverage_not_found(self, client: AsyncClient):
        resp = await client.get("/api/stories/doesnotexist/coverage")
        assert resp.status_code == 404

    @pytest.mark.asyncio
    async def test_get_articles_invalid_category(self, client: AsyncClient):
        resp = await client.get("/api/articles/?category=nonexistent")
        assert resp.status_code == 200
        assert resp.json() == []

    @pytest.mark.asyncio
    async def test_get_articles_limit_and_skip(
        self, client: AsyncClient, mock_db, sample_articles_list
    ):
        # Insert 5 articles
        for article in sample_articles_list[:5]:
            await mock_db.articles.insert_one(article)
        resp = await client.get("/api/articles/?limit=2&skip=1")
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, list)
        assert len(data) == 2

    @pytest.mark.asyncio
    async def test_ingest_articles_success(self, client: AsyncClient, monkeypatch):
        # Patch ingestion_service.ingest_all_sources to return a fake article (async)
        from app.routes.articles import ingestion_service

        class FakeArticle:
            def __init__(self):
                self.url = "http://fake.com/1"
                self.title = "Fake"
                self.content = "Fake content"
                self.model_dump = lambda: {
                    "url": self.url,
                    "title": self.title,
                    "content": self.content,
                }

        async def fake_ingest_all_sources():
            return [FakeArticle()]

        monkeypatch.setattr(
            ingestion_service, "ingest_all_sources", fake_ingest_all_sources
        )
        resp = await client.post("/api/articles/ingest")
        assert resp.status_code == 200
        assert "total_ingested" in resp.json()

    @pytest.mark.asyncio
    async def test_add_source_missing_params(self, client: AsyncClient):
        resp = await client.post(
            "/api/articles/sources/add", params={"name": "OnlyName"}
        )
        assert resp.status_code == 422

    @pytest.mark.asyncio
    async def test_get_story_coverage_zero_sources(
        self, client: AsyncClient, mock_db, sample_story_data
    ):
        # Insert story with no sources covered
        story = dict(sample_story_data)
        story["sources_covered"] = []
        await mock_db.stories.insert_one(story)
        resp = await client.get(f"/api/stories/{story['story_id']}/coverage")
        assert resp.status_code == 200
        data = resp.json()
        assert data["coverage_percentage"] == 0

    @pytest.mark.asyncio
    async def test_analytics_filter_by_date(
        self, client: AsyncClient, mock_db, sample_articles_list
    ):
        # Insert articles with different dates
        now = datetime.utcnow()
        for i, article in enumerate(sample_articles_list[:3]):
            article["published_date"] = (now - timedelta(days=i)).isoformat()
            await mock_db.articles.insert_one(article)
        start = (now - timedelta(days=1)).isoformat()
        end = now.isoformat()
        resp = await client.get(
            f"/api/analytics/filter?start_date={start}&end_date={end}"
        )
        assert resp.status_code == 200
        data = resp.json()
        # Compare as ISO strings
        assert all(start <= a["published_date"] <= end for a in data)

    @pytest.mark.asyncio
    async def test_get_story_not_found_coverage(self, client: AsyncClient):
        resp = await client.get("/api/stories/doesnotexist/coverage")
        assert resp.status_code == 404
        assert resp.json()["detail"] == "Story not found"

    @pytest.mark.asyncio
    async def test_get_fact_ledger_not_found(self, client: AsyncClient):
        resp = await client.get("/api/fact-checker/doesnotexist")
        assert resp.status_code == 404
        assert "Fact ledger not found" in resp.json()["detail"]
