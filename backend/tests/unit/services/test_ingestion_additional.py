"""
Unit tests for additional ingestion parsing edge cases.
"""

from unittest.mock import Mock
from app.services.ingestion import NewsIngestionService


def test_parse_rss_entry_nonstring_author_and_missing_tag():
    service = NewsIngestionService()

    entry = Mock()
    entry.link = "https://example.com/article"
    entry.title = "Test"
    entry.summary = "Summary"
    entry.published_parsed = (2025, 12, 15, 12, 0, 0, 0, 0, 0)

    # Author is not a string (e.g., an object), should be treated as None
    entry.author = Mock()

    # tags present but tag.term missing
    tag = Mock()
    delattr(tag, "term") if hasattr(tag, "term") else None
    entry.tags = [tag]

    source = {
        "name": "Test",
        "url": "https://example.com",
        "ideology": "center",
        "geography": "US",
    }

    article = service._parse_rss_entry(entry, source)
    assert article is not None
    assert article.author is None
    assert article.category is None


def test_parse_rss_entry_description_used_when_no_summary():
    service = NewsIngestionService()

    entry = Mock()
    entry.link = "https://example.com/article-desc"
    entry.title = "Desc Article"
    entry.summary = None
    entry.description = "<div>Desc content</div>"
    entry.published_parsed = (2025, 12, 15, 12, 0, 0, 0, 0, 0)

    source = {
        "name": "Test",
        "url": "https://example.com",
        "ideology": "center",
        "geography": "US",
    }

    article = service._parse_rss_entry(entry, source)
    assert article is not None
    assert "Desc content" in article.content
