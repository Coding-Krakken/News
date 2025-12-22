import pytest
from datetime import datetime, timedelta
from fastapi import BackgroundTasks

from app.routes import stories


@pytest.mark.asyncio
async def test_cluster_articles_background_with_old_articles(monkeypatch, capsys):
    # Articles older than time window should result in 0 clustered stories
    old_article = {
        "url": "http://old",
        "title": "old",
        "content": "c",
        "source_name": "S",
        "source_url": "u",
        "published_date": datetime.utcnow() - timedelta(hours=500),
    }

    class Cursor:
        def __init__(self, data):
            self._data = data

        async def to_list(self, length=None):
            return self._data

    class Collection:
        def __init__(self, data):
            self._data = data

        def find(self, *a, **k):
            return Cursor(self._data)

        async def update_one(self, *a, **k):
            return None

    class DB:
        def __init__(self):
            self.stories = Collection([])
            self.articles = Collection([old_article])

    monkeypatch.setattr(stories, "get_database", lambda: DB())

    # Should not raise and should print clustering result
    await stories.cluster_articles_background()
    out = capsys.readouterr().out
    assert "Clustered" in out


@pytest.mark.asyncio
async def test_trigger_clustering_endpoint_background_tasks():
    bt = BackgroundTasks()
    result = await stories.trigger_clustering(bt)
    assert isinstance(result, dict) and result.get("message")
