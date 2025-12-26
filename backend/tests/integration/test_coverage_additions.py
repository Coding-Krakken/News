"""
Additional integration tests to exercise error branches and low-coverage routes.
"""

import pytest
from httpx import AsyncClient
from unittest.mock import AsyncMock


@pytest.mark.integration
class TestCoverageAdditions:

    @pytest.mark.asyncio
    async def test_root_endpoint(self, client: AsyncClient):
        resp = await client.get("/")
        assert resp.status_code == 200
        data = resp.json()
        assert "message" in data and "version" in data

    @pytest.mark.asyncio
    async def test_ingest_handles_db_update_error(
        self, client: AsyncClient, mock_db, monkeypatch
    ):
        # Patch ingestion service to return one fake article-like object
        from app.routes.articles import ingestion_service

        class FakeArticle:
            def __init__(self):
                self.url = "http://fake.example/1"
                self.title = "Fake"
                self.content = "Fake content"

            def model_dump(self):
                return {"url": self.url, "title": self.title, "content": self.content}

        async def fake_ingest_all_sources():
            return [FakeArticle()]

        monkeypatch.setattr(
            ingestion_service, "ingest_all_sources", fake_ingest_all_sources
        )

        # Make the DB update_one raise to hit the inner except branch
        async def raise_update(*args, **kwargs):
            raise Exception("update failed")

        monkeypatch.setattr(
            mock_db.articles, "update_one", AsyncMock(side_effect=raise_update)
        )

        resp = await client.post("/api/articles/ingest")
        assert resp.status_code == 200
        data = resp.json()
        # Should have handled the DB error; at minimum return an integer total_ingested
        assert "total_ingested" in data
        assert isinstance(data["total_ingested"], int)

    @pytest.mark.asyncio
    async def test_analytics_facets_handles_db_error(self, monkeypatch):
        # Directly call the route function with a fake DB whose distinct raises to test exception branch
        from fastapi import HTTPException
        import app.routes.analytics as analytics_module

        class BrokenArticles:
            async def distinct(self, *args, **kwargs):
                raise Exception("distinct error")

        class FakeDB:
            def __init__(self):
                self.articles = BrokenArticles()

        with pytest.raises(HTTPException) as excinfo:
            await analytics_module.get_filter_facets(db=FakeDB())

        assert excinfo.value.status_code == 500
        assert "distinct error" in excinfo.value.detail

    @pytest.mark.asyncio
    async def test_fact_checker_handles_service_error(
        self,
        client: AsyncClient,
        mock_db,
        sample_story_data,
        sample_articles_list,
        monkeypatch,
    ):
        # Insert story and articles
        await mock_db.stories.insert_one(sample_story_data)
        for i, article_url in enumerate(sample_story_data["article_ids"]):
            article_data = sample_articles_list[i].copy()
            article_data["url"] = article_url
            await mock_db.articles.insert_one(article_data)

        # Patch the fact checker to raise
        from app.routes.fact_checker import fact_checker

        async def raise_generate(*args, **kwargs):
            raise Exception("fact error")

        monkeypatch.setattr(
            fact_checker, "generate_fact_ledger", AsyncMock(side_effect=raise_generate)
        )

        resp = await client.post(f"/api/fact-checker/{sample_story_data['story_id']}")
        assert resp.status_code == 500
        assert "fact error" in resp.json()["detail"]

    @pytest.mark.asyncio
    async def test_cluster_background_handles_exceptions(self, mock_db, monkeypatch):
        # Call the background clustering function directly while forcing the clustering service to raise
        from app.routes import stories

        # Ensure the module uses our mock DB
        monkeypatch.setattr(stories, "get_database", lambda: mock_db)

        def raise_cluster(_):
            raise Exception("cluster fail")

        monkeypatch.setattr(
            stories.clustering_service, "cluster_articles", raise_cluster
        )

        # Calling the async background function should not raise (it catches exceptions)
        await stories.cluster_articles_background()
