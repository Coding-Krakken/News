import pytest
from types import SimpleNamespace
from app.routes import articles


class BadDB:
    def __init__(self):
        pass

    async def update_one(self, *a, **k):
        raise RuntimeError("insert fail")

    def __getattr__(self, name):
        return self

    def find(self, *a, **k):
        class C:
            async def to_list(self, length=None):
                return []

        return C()


@pytest.mark.asyncio
async def test_ingest_articles_handles_insert_exceptions(monkeypatch):
    # Force ingestion to return one article
    fake_article = SimpleNamespace()
    fake_article.url = "http://a"
    fake_article.title = "t"
    fake_article.content = "c"
    fake_article.model_dump = lambda: {"url": fake_article.url}

    monkeypatch.setattr(articles, "ingestion_service", articles.ingestion_service)

    async def fake_ingest():
        return [fake_article]

    monkeypatch.setattr(articles.ingestion_service, "ingest_all_sources", fake_ingest)

    db = BadDB()
    res = await articles.ingest_articles(db=db)
    assert res["total_ingested"] == 0
