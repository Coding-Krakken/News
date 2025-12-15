"""
Unit tests for analytics service.
"""
import pytest
from datetime import datetime, timedelta
from app.services.analytics import AnalyticsService
from app.models.schemas import Article, Story, CoverageStats


class TestAnalyticsService:
    """Test AnalyticsService functionality."""
    
    @pytest.fixture
    def service(self):
        """Provide analytics service instance."""
        return AnalyticsService()
    
    def test_compute_coverage_stats_empty(self, service):
        """Test computing stats with empty data."""
        stats = service.compute_coverage_stats([], [])
        
        assert isinstance(stats, CoverageStats)
        assert stats.total_articles == 0
        assert stats.total_stories == 0
        assert stats.by_source == {}
    
    def test_compute_coverage_stats_by_source(self, service, sample_articles_list):
        """Test computing coverage stats by source."""
        articles = [Article(**data) for data in sample_articles_list]
        
        stats = service.compute_coverage_stats(articles, [])
        
        assert stats.total_articles == len(articles)
        assert len(stats.by_source) > 0
        assert "Source 0" in stats.by_source
        assert "Source 1" in stats.by_source
    
    def test_compute_coverage_stats_by_category(self, service, sample_articles_list):
        """Test computing coverage stats by category."""
        articles = [Article(**data) for data in sample_articles_list]
        
        # Set categories
        articles[0].category = "tech"
        articles[1].category = "tech"
        articles[2].category = "politics"
        
        stats = service.compute_coverage_stats(articles, [])
        
        assert "tech" in stats.by_category
        assert "politics" in stats.by_category
        assert stats.by_category["tech"] == 2
        assert stats.by_category["politics"] == 1
    
    def test_compute_coverage_stats_by_geography(self, service, sample_articles_list):
        """Test computing coverage stats by geography."""
        articles = [Article(**data) for data in sample_articles_list]
        
        # Set geographies
        articles[0].geography = "United States"
        articles[1].geography = "United Kingdom"
        articles[2].geography = "United States"
        
        stats = service.compute_coverage_stats(articles, [])
        
        assert "United States" in stats.by_geography
        assert "United Kingdom" in stats.by_geography
        assert stats.by_geography["United States"] == 2
    
    def test_compute_coverage_stats_by_ideology(self, service, sample_articles_list):
        """Test computing coverage stats by ideology."""
        articles = [Article(**data) for data in sample_articles_list]
        
        # Set ideologies
        articles[0].ideology = "left"
        articles[1].ideology = "center"
        articles[2].ideology = "right"
        articles[3].ideology = "center"
        
        stats = service.compute_coverage_stats(articles, [])
        
        assert "left" in stats.by_ideology
        assert "center" in stats.by_ideology
        assert "right" in stats.by_ideology
        assert stats.by_ideology["center"] == 2
    
    def test_compute_time_stats_recent_articles(self, service, sample_articles_list):
        """Test computing time stats for recent articles."""
        articles = [Article(**data) for data in sample_articles_list]
        
        # Set recent timestamps
        now = datetime.utcnow()
        articles[0].published_date = now - timedelta(hours=2)
        articles[1].published_date = now - timedelta(hours=5)
        articles[2].published_date = now - timedelta(hours=48)
        
        time_stats = service._compute_time_stats(articles)
        
        assert "2h ago" in time_stats or any("h ago" in k for k in time_stats.keys())
    
    def test_compute_time_stats_old_articles(self, service, sample_articles_list):
        """Test computing time stats for old articles."""
        articles = [Article(**data) for data in sample_articles_list]
        
        # Set old timestamps
        now = datetime.utcnow()
        articles[0].published_date = now - timedelta(days=30)
        
        time_stats = service._compute_time_stats(articles)
        
        assert "older" in time_stats
    
    def test_get_story_coverage_matrix(self, service, sample_story_data):
        """Test getting coverage matrix for a story."""
        story = Story(**sample_story_data)
        all_sources = ["Source A", "Source B", "Source C", "Source D"]
        
        matrix = service.get_story_coverage_matrix(story, all_sources)
        
        assert len(matrix) == 4
        assert matrix["Source A"] is True
        assert matrix["Source B"] is True
        assert matrix["Source C"] is False
        assert matrix["Source D"] is False
    
    def test_filter_articles_by_sources(self, service, sample_articles_list):
        """Test filtering articles by sources."""
        articles = [Article(**data) for data in sample_articles_list]
        
        filtered = service.filter_articles(articles, sources=["Source 0"])
        
        assert len(filtered) < len(articles)
        assert all(a.source_name == "Source 0" for a in filtered)
    
    def test_filter_articles_by_categories(self, service, sample_articles_list):
        """Test filtering articles by categories."""
        articles = [Article(**data) for data in sample_articles_list]
        
        articles[0].category = "tech"
        articles[1].category = "politics"
        articles[2].category = "tech"
        
        filtered = service.filter_articles(articles, categories=["tech"])
        
        assert len(filtered) == 2
        assert all(a.category == "tech" for a in filtered)
    
    def test_filter_articles_by_geographies(self, service, sample_articles_list):
        """Test filtering articles by geographies."""
        articles = [Article(**data) for data in sample_articles_list]
        
        articles[0].geography = "US"
        articles[1].geography = "UK"
        articles[2].geography = "US"
        
        filtered = service.filter_articles(articles, geographies=["US"])
        
        assert len(filtered) == 2
        assert all(a.geography == "US" for a in filtered)
    
    def test_filter_articles_by_ideologies(self, service, sample_articles_list):
        """Test filtering articles by ideologies."""
        articles = [Article(**data) for data in sample_articles_list]
        
        articles[0].ideology = "left"
        articles[1].ideology = "center"
        articles[2].ideology = "right"
        
        filtered = service.filter_articles(articles, ideologies=["center", "right"])
        
        assert len(filtered) == 2
        assert all(a.ideology in ["center", "right"] for a in filtered)
    
    def test_filter_articles_by_date_range(self, service, sample_articles_list):
        """Test filtering articles by date range."""
        articles = [Article(**data) for data in sample_articles_list]
        
        now = datetime.utcnow()
        start_date = now - timedelta(hours=3)
        end_date = now
        
        # Set dates to be within and outside range
        articles[0].published_date = now - timedelta(hours=2)  # Within
        articles[1].published_date = now - timedelta(hours=5)  # Outside
        articles[2].published_date = now - timedelta(hours=1)  # Within
        
        filtered = service.filter_articles(
            articles,
            start_date=start_date,
            end_date=end_date
        )
        
        assert len(filtered) == 2
    
    def test_filter_articles_multiple_criteria(self, service, sample_articles_list):
        """Test filtering articles by multiple criteria."""
        articles = [Article(**data) for data in sample_articles_list]
        
        # Set specific attributes
        articles[0].source_name = "Source A"
        articles[0].category = "tech"
        articles[1].source_name = "Source A"
        articles[1].category = "politics"
        articles[2].source_name = "Source B"
        articles[2].category = "tech"
        
        filtered = service.filter_articles(
            articles,
            sources=["Source A"],
            categories=["tech"]
        )
        
        # Should match both criteria
        assert len(filtered) == 1
        assert filtered[0].source_name == "Source A"
        assert filtered[0].category == "tech"
    
    def test_filter_articles_no_matches(self, service, sample_articles_list):
        """Test filtering with no matching articles."""
        articles = [Article(**data) for data in sample_articles_list]
        
        filtered = service.filter_articles(
            articles,
            sources=["Nonexistent Source"]
        )
        
        assert len(filtered) == 0
    
    def test_filter_articles_no_filters(self, service, sample_articles_list):
        """Test that no filters returns all articles."""
        articles = [Article(**data) for data in sample_articles_list]
        
        filtered = service.filter_articles(articles)
        
        assert len(filtered) == len(articles)
