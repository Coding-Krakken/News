"""
Unit tests for stories route helper to cover background clustering happy path.
"""

import pytest


@pytest.mark.asyncio
async def test_cluster_articles_background_success(monkeypatch):
    from app.routes import stories

    # Fake DB with articles list and update_one methods
    class FakeCursor:
        def __init__(self, data):
            self._data = data

        async def to_list(self, length=None):
            return self._data

    class FakeArticles:
        def __init__(self, data):
            self._data = data

        def find(self, *args, **kwargs):
            return FakeCursor(self._data)

        async def update_one(self, *args, **kwargs):
            return None

    class FakeStories:
        async def update_one(self, *args, **kwargs):
            return None

    class FakeDB:
        def __init__(self, data):
            self.articles = FakeArticles(data)
            self.stories = FakeStories()

    # Provide one mock article dict
    article_dict = {
        "url": "https://example.com/a1",
        "title": "A1",
        "content": "c",
        "source_name": "S",
        "published_date": None,
        "category": None,
        "geography": None,
        "ideology": None,
        "tags": [],
    }

    fake_db = FakeDB([article_dict])

    # Monkeypatch get_database to return our fake DB
    monkeypatch.setattr(stories, "get_database", lambda: fake_db)

    # Patch clustering service to return no stories (so loops are skipped)
    monkeypatch.setattr(stories.clustering_service, "cluster_articles", lambda x: [])

    # Call the background function; it should complete without raising
    await stories.cluster_articles_background()
