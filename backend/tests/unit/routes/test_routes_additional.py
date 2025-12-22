"""
Unit tests for route error branches to increase coverage.
"""
import pytest
from fastapi import HTTPException


def test_articles_get_raises_on_db_error(monkeypatch):
    from app.routes import articles

    class BrokenCursor:
        async def to_list(self, length=None):
            raise Exception("db find error")

    class FakeDB:
        def __init__(self):
            self.articles = self
        def find(self, *args, **kwargs):
            return BrokenCursor()

    # Call the route function directly and assert it raises HTTPException
    with pytest.raises(HTTPException) as excinfo:
        awaitable = articles.get_articles(db=FakeDB())
        # get_articles is async
        import asyncio
        asyncio.get_event_loop().run_until_complete(awaitable)

    assert excinfo.value.status_code == 500


def test_add_source_handles_service_error(monkeypatch):
    from app.routes import articles

    def broken_add(*args, **kwargs):
        raise Exception("add failure")

    monkeypatch.setattr(articles.ingestion_service, "add_source", broken_add)

    # Call add_source directly and expect HTTPException
    import asyncio
    coro = articles.add_source(name="X", url="u")
    with pytest.raises(HTTPException) as excinfo:
        asyncio.get_event_loop().run_until_complete(coro)

    assert excinfo.value.status_code == 500


def test_ingest_articles_handles_outer_exception(monkeypatch):
    from app.routes import articles

    async def bad_ingest():
        raise Exception("ingest outer")

    monkeypatch.setattr(articles.ingestion_service, "ingest_all_sources", bad_ingest)

    import asyncio
    coro = articles.ingest_articles()
    with pytest.raises(HTTPException) as excinfo:
        asyncio.get_event_loop().run_until_complete(coro)

    assert excinfo.value.status_code == 500
