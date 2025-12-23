
import pytest

pytestmark = pytest.mark.asyncio

@pytest.mark.integration
class TestArticlesEdgeCases:
    async def test_get_articles_invalid_params(self, client):
        # Invalid limit (too high)
        resp = await client.get("/api/articles/?limit=1000")
        assert resp.status_code == 422
        # Invalid skip (negative)
        resp = await client.get("/api/articles/?skip=-1")
        assert resp.status_code == 422

    async def test_get_article_not_found(self, client):
        resp = await client.get("/api/articles/nonexistent-url")
        assert resp.status_code == 404
        assert resp.json()["detail"] == "Article not found"

    async def test_add_source_duplicate(self, client):
        # Add a source
        data = {
            "name": "TestSource",
            "url": "http://example.com/rss",
            "source_type": "rss",
            "ideology": "center",
            "geography": "TestLand"
        }
        resp = await client.post("/api/articles/sources/add", params=data)
        assert resp.status_code == 200
        # Add again (should not error, but will duplicate in-memory)
        resp2 = await client.post("/api/articles/sources/add", params=data)
        assert resp2.status_code == 200

@pytest.mark.integration
class TestAnalyticsEdgeCases:
    async def test_filter_articles_invalid_date(self, client):
        # Invalid date format
        resp = await client.get("/api/analytics/filter?start_date=notadate")
        assert resp.status_code == 422 or resp.status_code == 500

    async def test_get_facets_empty(self, client):
        resp = await client.get("/api/analytics/facets")
        assert resp.status_code == 200
        data = resp.json()
        assert "sources" in data and isinstance(data["sources"], list)

@pytest.mark.integration
class TestStoriesEdgeCases:
    async def test_get_story_not_found(self, client):
        resp = await client.get("/api/stories/doesnotexist")
        assert resp.status_code == 404
        assert resp.json()["detail"] == "Story not found"

    async def test_get_story_articles_not_found(self, client):
        resp = await client.get("/api/stories/doesnotexist/articles")
        assert resp.status_code == 404

    async def test_get_story_coverage_not_found(self, client):
        resp = await client.get("/api/stories/doesnotexist/coverage")
        assert resp.status_code == 404

@pytest.mark.integration
class TestFactCheckerEdgeCases:
    async def test_get_fact_ledger_not_found(self, client):
        resp = await client.get("/api/fact-checker/doesnotexist")
        assert resp.status_code == 404
        assert "Fact ledger not found" in resp.json()["detail"]

    async def test_generate_fact_ledger_story_not_found(self, client):
        resp = await client.post("/api/fact-checker/doesnotexist")
        assert resp.status_code == 404
        assert resp.json()["detail"] == "Story not found"
