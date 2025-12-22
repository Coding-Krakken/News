"""
Unit tests for data models and schemas.
"""
import pytest
from datetime import datetime
from pydantic import ValidationError
from app.models.schemas import (
    Article,
    Story,
    Claim,
    FactLedger,
    CoverageStats
)


class TestArticleModel:
    """Test Article model validation and serialization."""
    
    def test_article_creation_with_valid_data(self, sample_article_data):
        """Test creating an article with valid data."""
        article = Article(**sample_article_data)
        assert article.url == sample_article_data["url"]
        assert article.title == sample_article_data["title"]
        assert article.source_name == sample_article_data["source_name"]
    
    def test_article_requires_mandatory_fields(self):
        """Test that article requires mandatory fields."""
        with pytest.raises(ValidationError):
            Article(url="https://example.com")
    
    def test_article_with_minimal_data(self):
        """Test creating article with minimal required fields."""
        article = Article(
            url="https://example.com/article",
            title="Test Title",
            content="Test content",
            source_name="Test Source",
            source_url="https://example.com",
            published_date=datetime.utcnow()
        )
        assert article.url == "https://example.com/article"
        assert article.tags == []  # Default value
        assert article.embedding is None  # Default value
    
    def test_article_default_created_at(self):
        """Test that created_at has a default value."""
        article = Article(
            url="https://example.com/article",
            title="Test",
            content="Test",
            source_name="Test",
            source_url="https://example.com",
            published_date=datetime.utcnow()
        )
        assert isinstance(article.created_at, datetime)
    
    def test_article_with_embedding(self, sample_article_data):
        """Test article with embedding vector."""
        sample_article_data["embedding"] = [0.1, 0.2, 0.3]
        article = Article(**sample_article_data)
        assert len(article.embedding) == 3
        assert article.embedding[0] == 0.1


class TestStoryModel:
    """Test Story model validation and serialization."""
    
    def test_story_creation_with_valid_data(self, sample_story_data):
        """Test creating a story with valid data."""
        story = Story(**sample_story_data)
        assert story.story_id == sample_story_data["story_id"]
        assert story.title == sample_story_data["title"]
        assert len(story.article_ids) == 2
    
    def test_story_requires_mandatory_fields(self):
        """Test that story requires mandatory fields."""
        with pytest.raises(ValidationError):
            Story(story_id="test123")
    
    def test_story_default_values(self):
        """Test story default values."""
        story = Story(
            story_id="test123",
            title="Test Story",
            summary="Summary",
            article_ids=["url1"],
            sources_covered=["Source A"],
            first_seen=datetime.utcnow(),
            last_updated=datetime.utcnow()
        )
        assert story.sources_not_covered == []
        assert story.geographies == []
        assert story.ideologies == []
        assert story.article_count == 0
    
    def test_story_with_multiple_sources(self, sample_story_data):
        """Test story with multiple sources."""
        sample_story_data["sources_covered"] = ["A", "B", "C"]
        sample_story_data["sources_not_covered"] = ["D", "E"]
        story = Story(**sample_story_data)
        assert len(story.sources_covered) == 3
        assert len(story.sources_not_covered) == 2


class TestClaimModel:
    """Test Claim model validation and serialization."""
    
    def test_claim_creation(self, sample_claim):
        """Test creating a claim."""
        claim = Claim(**sample_claim)
        assert claim.text == sample_claim["text"]
        assert claim.attribution == sample_claim["attribution"]
        assert claim.is_confirmed is False
    
    def test_claim_confirmed_state(self, sample_claim):
        """Test claim in confirmed state."""
        sample_claim["is_confirmed"] = True
        sample_claim["supporting_sources"] = ["Source A", "Source B"]
        sample_claim["corroboration_count"] = 2
        claim = Claim(**sample_claim)
        assert claim.is_confirmed is True
        assert len(claim.supporting_sources) == 2
    
    def test_claim_disputed_state(self, sample_claim):
        """Test claim in disputed state."""
        sample_claim["is_disputed"] = True
        sample_claim["disputing_sources"] = ["Source X"]
        claim = Claim(**sample_claim)
        assert claim.is_disputed is True
        assert len(claim.disputing_sources) == 1
    
    def test_claim_default_lists(self):
        """Test claim default empty lists."""
        claim = Claim(
            text="Test claim",
            attribution="Source",
            article_url="https://example.com"
        )
        assert claim.supporting_sources == []
        assert claim.disputing_sources == []


class TestFactLedgerModel:
    """Test FactLedger model validation and serialization."""
    
    def test_fact_ledger_creation(self, sample_claim):
        """Test creating a fact ledger."""
        ledger = FactLedger(
            story_id="story123",
            confirmed_claims=[Claim(**sample_claim)],
            disputed_claims=[],
            uncorroborated_claims=[]
        )
        assert ledger.story_id == "story123"
        assert len(ledger.confirmed_claims) == 1
        assert isinstance(ledger.generated_at, datetime)
    
    def test_fact_ledger_with_all_claim_types(self, sample_claim):
        """Test fact ledger with all claim types."""
        confirmed = sample_claim.copy()
        confirmed["is_confirmed"] = True
        
        disputed = sample_claim.copy()
        disputed["is_disputed"] = True
        disputed["text"] = "Disputed claim"
        
        uncorroborated = sample_claim.copy()
        uncorroborated["text"] = "Uncorroborated claim"
        
        ledger = FactLedger(
            story_id="story123",
            confirmed_claims=[Claim(**confirmed)],
            disputed_claims=[Claim(**disputed)],
            uncorroborated_claims=[Claim(**uncorroborated)]
        )
        assert len(ledger.confirmed_claims) == 1
        assert len(ledger.disputed_claims) == 1
        assert len(ledger.uncorroborated_claims) == 1
    
    def test_fact_ledger_empty(self):
        """Test empty fact ledger."""
        ledger = FactLedger(story_id="story123")
        assert ledger.confirmed_claims == []
        assert ledger.disputed_claims == []
        assert ledger.uncorroborated_claims == []


class TestCoverageStatsModel:
    """Test CoverageStats model validation and serialization."""
    
    def test_coverage_stats_creation(self):
        """Test creating coverage stats."""
        stats = CoverageStats(
            total_articles=100,
            total_stories=20
        )
        assert stats.total_articles == 100
        assert stats.total_stories == 20
    
    def test_coverage_stats_with_data(self):
        """Test coverage stats with dimension data."""
        stats = CoverageStats(
            by_source={"Source A": 50, "Source B": 50},
            by_category={"tech": 30, "politics": 70},
            by_geography={"US": 60, "UK": 40},
            by_ideology={"left": 30, "center": 40, "right": 30},
            by_time={"0h ago": 10, "1h ago": 20},
            total_articles=100,
            total_stories=20
        )
        assert len(stats.by_source) == 2
        assert stats.by_source["Source A"] == 50
        assert len(stats.by_category) == 2
    
    def test_coverage_stats_default_values(self):
        """Test coverage stats default values."""
        stats = CoverageStats()
        assert stats.by_source == {}
        assert stats.by_category == {}
        assert stats.total_articles == 0
        assert stats.total_stories == 0
