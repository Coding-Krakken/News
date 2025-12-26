import pytest
from datetime import datetime

from app.routes import stories
from app.models.schemas import Story


class FakeCursor:
    def __init__(self, data):
        self._data = data

    async def to_list(self, length=None):
        return self._data


class FakeDB:
    def __init__(self, articles_data=None, story=None, distinct_values=None):
        self._articles = articles_data or []
        self._story = story
        self._distinct = distinct_values or []
        self.updated = []

    def articles_find(self, *args, **kwargs):
        return FakeCursor(self._articles)

    def stories_find(self, *args, **kwargs):
        return FakeCursor([])

    def articles(self):
        return self

    def stories(self):
        return self

    def find(self, *args, **kwargs):
        # used for both articles.find and stories.find
        return FakeCursor(
            self._articles if kwargs.get("collection") != "stories" else []
        )

    async def find_one(self, query, projection=None):
        return self._story

    async def update_one(self, *args, **kwargs):
        self.updated.append((args, kwargs))

    async def distinct(self, field):
        return self._distinct


def make_article_dict(url="http://example.com/a", title="T", content="C"):
    return {
        "url": url,
        "title": title,
        "content": content,
        "source_name": "S",
        "source_url": "http://s",
        "published_date": datetime.utcnow(),
    }


@pytest.mark.asyncio
async def test_cluster_articles_background_success(monkeypatch):
    # Prepare one article and a story returned by clustering
    articles_data = [make_article_dict()]

    fake_db = FakeDB(articles_data=articles_data)

    def fake_get_db():
        return fake_db

    # Replace get_database used in module
    monkeypatch.setattr(stories, "get_database", fake_get_db)

    # Make clustering return a Story object
    story = Story(
        story_id="s1",
        title="s",
        summary="sum",
        article_ids=[articles_data[0]["url"]],
        sources_covered=["S"],
        first_seen=datetime.utcnow(),
        last_updated=datetime.utcnow(),
        article_count=1,
    )

    monkeypatch.setattr(stories, "clustering_service", stories.clustering_service)
    monkeypatch.setattr(
        stories.clustering_service, "cluster_articles", lambda x: [story]
    )

    # Should not raise
    await stories.cluster_articles_background()


@pytest.mark.asyncio
async def test_cluster_articles_background_handles_exception(monkeypatch, capsys):
    # Force clustering to raise to hit the exception branch
    fake_db = FakeDB(articles_data=[make_article_dict()])

    def fake_get_db():
        return fake_db

    monkeypatch.setattr(stories, "get_database", fake_get_db)

    def raise_exc(_):
        raise RuntimeError("boom")

    monkeypatch.setattr(stories.clustering_service, "cluster_articles", raise_exc)

    # Should swallow exception and print
    await stories.cluster_articles_background()
    captured = capsys.readouterr()
    assert "Error in background clustering" in captured.out


@pytest.mark.asyncio
async def test_get_story_coverage_division_by_zero(monkeypatch):
    # Story exists but there are no sources in articles -> coverage_percentage should be 0
    story_obj = {"story_id": "s1", "sources_covered": []}

    class DB:
        class Stories:
            async def find_one(self, q, p=None):
                return story_obj

        class Articles:
            async def distinct(self, field):
                return []

        def __init__(self):
            self.stories = DB.Stories()
            self.articles = DB.Articles()

    db = DB()
    res = await stories.get_story_coverage("s1", db=db)
    assert res["coverage_percentage"] == 0


@pytest.mark.asyncio
async def test_get_story_coverage_not_found(monkeypatch):
    class DB:
        class Stories:
            async def find_one(self, q, p=None):
                return None

        def __init__(self):
            self.stories = DB.Stories()

    db = DB()
    import fastapi

    with pytest.raises(fastapi.HTTPException) as ei:
        await stories.get_story_coverage("s2", db=db)
    assert ei.value.status_code == 404
