from types import SimpleNamespace
from app.services.ingestion import NewsIngestionService


def test_parse_rss_entry_returns_none_when_missing_url_or_title():
    svc = NewsIngestionService()
    entry = SimpleNamespace()
    # no link or title
    res = svc._parse_rss_entry(
        entry, {"name": "X", "url": "u", "geography": None, "ideology": None}
    )
    assert res is None
