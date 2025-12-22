import pytest
from app.services.ingestion import NewsIngestionService
from types import SimpleNamespace
from datetime import datetime


def make_entry(link="http://ex", title="T", summary=None, description=None, tags=None, author=None, published_parsed=None):
    obj = SimpleNamespace()
    obj.link = link
    obj.title = title
    if summary is not None:
        obj.summary = summary
    if description is not None:
        obj.description = description
    if tags is not None:
        obj.tags = tags
    if author is not None:
        obj.author = author
    if published_parsed is not None:
        obj.published_parsed = published_parsed
    return obj


def test_parse_rss_entry_tag_term_missing_and_nonstring_author():
    svc = NewsIngestionService()
    # tag object without .term
    tag_obj = SimpleNamespace()
    entry = make_entry(summary="<p>content</p>", tags=[tag_obj], author=object())
    art = svc._parse_rss_entry(entry, {"name": "X", "url": "u", "geography": None, "ideology": None})
    assert art is not None
    assert art.category is None
    assert art.author is None


def test_parse_rss_entry_uses_description_when_no_summary():
    svc = NewsIngestionService()
    entry = make_entry(description="<div>desc</div>")
    art = svc._parse_rss_entry(entry, {"name": "X", "url": "u", "geography": None, "ideology": None})
    assert art is not None
    assert "desc" in (art.content or "")
