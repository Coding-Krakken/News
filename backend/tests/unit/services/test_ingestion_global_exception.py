import pytest
from app.services.ingestion import NewsIngestionService


class BadEntry:
    def __getattr__(self, name):
        raise RuntimeError("boom")


def test_parse_rss_entry_global_exception_returns_none():
    svc = NewsIngestionService()
    entry = BadEntry()
    res = svc._parse_rss_entry(entry, {"name": "X", "url": "u", "geography": None, "ideology": None})
    assert res is None
