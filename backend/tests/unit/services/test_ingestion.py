"""
Unit tests for news ingestion service.
"""
import pytest
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime
from app.services.ingestion import NewsIngestionService
from app.models.schemas import Article


class TestNewsIngestionService:
    """Test NewsIngestionService functionality."""
    
    @pytest.fixture
    def service(self):
        """Provide ingestion service instance."""
        return NewsIngestionService()
    
    def test_service_initialization(self, service):
        """Test service initializes with sources."""
        assert len(service.sources) == 4
        assert service.sources[0]["name"] == "BBC News"
    
    def test_get_sources(self, service):
        """Test getting configured sources."""
        sources = service.get_sources()
        assert len(sources) == 4
        assert all("name" in s for s in sources)
        assert all("url" in s for s in sources)
    
    def test_add_source(self, service):
        """Test adding a new source."""
        initial_count = len(service.sources)
        service.add_source(
            name="Test Source",
            url="https://test.com/rss",
            source_type="rss",
            ideology="center",
            geography="Test Country"
        )
        assert len(service.sources) == initial_count + 1
        assert service.sources[-1]["name"] == "Test Source"
        assert service.sources[-1]["ideology"] == "center"
    
    def test_parse_rss_entry_valid(self, service):
        """Test parsing a valid RSS entry."""
        import feedparser
        
        # Create a mock entry
        entry = Mock()
        entry.link = "https://example.com/article"
        entry.title = "Test Article"
        entry.summary = "<p>Test summary</p>"
        entry.published_parsed = (2025, 12, 15, 12, 0, 0, 0, 0, 0)
        
        source = {
            "name": "Test Source",
            "url": "https://example.com/rss",
            "ideology": "center",
            "geography": "United States"
        }
        
        article = service._parse_rss_entry(entry, source)
        
        assert article is not None
        assert article.url == "https://example.com/article"
        assert article.title == "Test Article"
        assert article.source_name == "Test Source"
        assert article.ideology == "center"
    
    def test_parse_rss_entry_with_category(self, service):
        """Test parsing RSS entry with category."""
        entry = Mock()
        entry.link = "https://example.com/article"
        entry.title = "Test"
        entry.summary = "Summary"
        entry.published_parsed = (2025, 12, 15, 12, 0, 0, 0, 0, 0)
        
        tag = Mock()
        tag.term = "technology"
        entry.tags = [tag]
        
        source = {"name": "Test", "url": "https://example.com", "ideology": "center", "geography": "US"}
        
        article = service._parse_rss_entry(entry, source)
        assert article.category == "technology"
    
    def test_parse_rss_entry_with_author(self, service):
        """Test parsing RSS entry with author."""
        entry = Mock()
        entry.link = "https://example.com/article"
        entry.title = "Test"
        entry.summary = "Summary"
        entry.published_parsed = (2025, 12, 15, 12, 0, 0, 0, 0, 0)
        entry.author = "John Doe"
        
        source = {"name": "Test", "url": "https://example.com", "ideology": "center", "geography": "US"}
        
        article = service._parse_rss_entry(entry, source)
        assert article.author == "John Doe"
    
    def test_parse_rss_entry_invalid(self, service):
        """Test parsing invalid RSS entry returns None."""
        entry = Mock()
        entry.link = None  # Invalid: missing required field
        
        source = {"name": "Test", "url": "https://example.com"}
        
        article = service._parse_rss_entry(entry, source)
        assert article is None
    
    @pytest.mark.asyncio
    async def test_ingest_from_rss_success(self, service, mock_rss_feed):
        """Test successful RSS ingestion."""
        source = {
            "name": "Test Source",
            "url": "https://example.com/rss",
            "type": "rss",
            "ideology": "center",
            "geography": "United States"
        }
        
        with patch('aiohttp.ClientSession.get') as mock_get:
            # Mock the HTTP response
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.text = AsyncMock(return_value=mock_rss_feed)
            mock_get.return_value.__aenter__.return_value = mock_response
            
            articles = await service.ingest_from_rss(source)
            
            assert isinstance(articles, list)
            # Note: The actual parsing depends on feedparser
    
    @pytest.mark.asyncio
    async def test_ingest_from_rss_http_error(self, service):
        """Test RSS ingestion with HTTP error."""
        source = {
            "name": "Test Source",
            "url": "https://example.com/rss",
            "type": "rss",
            "ideology": "center",
            "geography": "United States"
        }
        
        with patch('aiohttp.ClientSession.get') as mock_get:
            mock_response = AsyncMock()
            mock_response.status = 404
            mock_get.return_value.__aenter__.return_value = mock_response
            
            articles = await service.ingest_from_rss(source)
            assert articles == []
    
    @pytest.mark.asyncio
    async def test_ingest_from_rss_timeout(self, service):
        """Test RSS ingestion with timeout."""
        source = {
            "name": "Test Source",
            "url": "https://example.com/rss",
            "type": "rss",
            "ideology": "center",
            "geography": "United States"
        }
        
        with patch('aiohttp.ClientSession.get') as mock_get:
            mock_get.side_effect = TimeoutError("Connection timeout")
            
            articles = await service.ingest_from_rss(source)
            assert articles == []
    
    @pytest.mark.asyncio
    async def test_ingest_all_sources(self, service):
        """Test ingesting from all sources."""
        with patch.object(service, 'ingest_from_rss', new_callable=AsyncMock) as mock_ingest:
            # Mock return articles for each source
            mock_article = Mock(spec=Article)
            mock_ingest.return_value = [mock_article]
            
            articles = await service.ingest_all_sources()
            
            # Should call ingest_from_rss for each source
            assert mock_ingest.call_count == 4
            assert len(articles) == 4
