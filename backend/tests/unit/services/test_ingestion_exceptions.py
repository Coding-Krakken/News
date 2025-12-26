from unittest.mock import Mock


def test_parse_rss_entry_handles_beautifulsoup_exception(monkeypatch):
    from app.services.ingestion import NewsIngestionService

    service = NewsIngestionService()

    # Patch BeautifulSoup to raise when called to exercise the except branch
    def raise_bs(*args, **kwargs):
        raise Exception("bs error")

    monkeypatch.setattr("app.services.ingestion.BeautifulSoup", raise_bs)

    entry = Mock()
    entry.link = "https://example.com/article"
    entry.title = "Test"
    entry.summary = "<p>Some <b>HTML</b></p>"
    entry.published_parsed = (2025, 12, 15, 12, 0, 0, 0, 0, 0)

    source = {
        "name": "Test",
        "url": "https://example.com",
        "ideology": "center",
        "geography": "US",
    }

    article = service._parse_rss_entry(entry, source)
    assert article is not None
    # When BeautifulSoup fails, content should fall back to str(summary)
    assert "Some" in article.content


def test_parse_rss_entry_handles_description_beautifulsoup_exception(monkeypatch):
    from app.services.ingestion import NewsIngestionService

    service = NewsIngestionService()

    def raise_bs(*args, **kwargs):
        raise Exception("bs error")

    monkeypatch.setattr("app.services.ingestion.BeautifulSoup", raise_bs)

    entry = Mock()
    entry.link = "https://example.com/article2"
    entry.title = "Test2"
    entry.summary = None
    entry.description = "<div>Desc</div>"
    entry.published_parsed = (2025, 12, 15, 12, 0, 0, 0, 0, 0)

    source = {
        "name": "Test",
        "url": "https://example.com",
        "ideology": "center",
        "geography": "US",
    }

    article = service._parse_rss_entry(entry, source)
    assert article is not None
    assert "Desc" in article.content
