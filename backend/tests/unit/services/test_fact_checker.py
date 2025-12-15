"""
Unit tests for fact-checking service.
"""
import pytest
from unittest.mock import Mock, patch, AsyncMock, MagicMock
from app.services.fact_checker import FactCheckingService
from app.models.schemas import Article, Claim, FactLedger


class TestFactCheckingService:
    """Test FactCheckingService functionality."""
    
    @pytest.fixture
    def service(self):
        """Provide fact-checking service instance."""
        return FactCheckingService()
    
    def test_service_initialization(self, service):
        """Test service initialization."""
        assert service.api_key is not None  # From conftest
    
    def test_simple_claim_extraction(self, service, sample_article_data):
        """Test simple rule-based claim extraction."""
        article = Article(**sample_article_data)
        article.content = "This is a claim. This is another claim. And a third claim."
        
        claims = service._simple_claim_extraction(article)
        
        assert isinstance(claims, list)
        assert len(claims) > 0
        assert all(isinstance(c, Claim) for c in claims)
        assert all(c.attribution == article.source_name for c in claims)
    
    def test_simple_claim_extraction_minimum_length(self, service, sample_article_data):
        """Test that simple extraction filters short sentences."""
        article = Article(**sample_article_data)
        article.content = "Short. This is a longer sentence that should be included."
        
        claims = service._simple_claim_extraction(article)
        
        # Short sentences should be filtered out
        assert all(len(c.text) > 20 for c in claims)
    
    def test_simple_claim_extraction_limit(self, service, sample_article_data):
        """Test that simple extraction limits number of claims."""
        article = Article(**sample_article_data)
        article.content = ". ".join([f"Claim number {i}" for i in range(20)])
        
        claims = service._simple_claim_extraction(article)
        
        # Should limit to first 5 sentences
        assert len(claims) <= 5
    
    @pytest.mark.asyncio
    async def test_extract_claims_from_article_with_ai(self, service, sample_article_data, mock_openai_response):
        """Test claim extraction with OpenAI API."""
        article = Article(**sample_article_data)
        
        with patch('openai.OpenAI') as mock_openai:
            mock_client = MagicMock()
            mock_completion = MagicMock()
            mock_completion.choices = [MagicMock()]
            mock_completion.choices[0].message.content = '[{"text": "Test claim", "is_factual": true}]'
            mock_client.chat.completions.create.return_value = mock_completion
            mock_openai.return_value = mock_client
            
            claims = await service._extract_claims_from_article(article)
            
            assert len(claims) > 0
            assert claims[0].text == "Test claim"
            assert claims[0].attribution == article.source_name
    
    @pytest.mark.asyncio
    async def test_extract_claims_from_article_ai_fallback(self, service, sample_article_data):
        """Test fallback to simple extraction when AI fails."""
        article = Article(**sample_article_data)
        
        with patch('openai.OpenAI') as mock_openai:
            mock_openai.side_effect = Exception("API Error")
            
            claims = await service._extract_claims_from_article(article)
            
            # Should fall back to simple extraction
            assert isinstance(claims, list)
    
    @pytest.mark.asyncio
    async def test_extract_claims_multiple_articles(self, service, sample_articles_list):
        """Test extracting claims from multiple articles."""
        articles = [Article(**data) for data in sample_articles_list[:2]]
        
        with patch.object(service, '_extract_claims_from_article', new_callable=AsyncMock) as mock_extract:
            mock_claim = Claim(
                text="Test claim",
                attribution="Source",
                article_url="https://example.com"
            )
            mock_extract.return_value = [mock_claim]
            
            claims = await service.extract_claims(articles)
            
            assert len(claims) == 2
            assert mock_extract.call_count == 2
    
    @pytest.mark.asyncio
    async def test_extract_claims_handles_errors(self, service, sample_articles_list):
        """Test that claim extraction handles errors gracefully."""
        articles = [Article(**data) for data in sample_articles_list[:2]]
        
        with patch.object(service, '_extract_claims_from_article', new_callable=AsyncMock) as mock_extract:
            # First call succeeds, second fails
            mock_claim = Claim(text="Test", attribution="Source", article_url="url")
            mock_extract.side_effect = [
                [mock_claim],
                Exception("Error")
            ]
            
            claims = await service.extract_claims(articles)
            
            # Should still return claims from successful extraction
            assert len(claims) == 1
    
    def test_are_claims_similar_identical(self, service):
        """Test similarity detection for identical claims."""
        text1 = "This is a test claim about something"
        text2 = "This is a test claim about something"
        
        result = service._are_claims_similar(text1, text2)
        assert result is True
    
    def test_are_claims_similar_high_overlap(self, service):
        """Test similarity detection for claims with high word overlap."""
        text1 = "The president announced new policy today"
        text2 = "The president announced new policy yesterday"
        
        result = service._are_claims_similar(text1, text2)
        assert result is True
    
    def test_are_claims_similar_different(self, service):
        """Test similarity detection for different claims."""
        text1 = "The weather is sunny today"
        text2 = "Stock market crashed yesterday"
        
        result = service._are_claims_similar(text1, text2)
        assert result is False
    
    def test_are_claims_similar_empty(self, service):
        """Test similarity with empty strings."""
        result = service._are_claims_similar("", "test")
        assert result is False
    
    def test_group_similar_claims_single_group(self, service, sample_claim):
        """Test grouping similar claims together."""
        claim1 = Claim(**sample_claim)
        claim1.text = "This is a factual claim about topic"
        
        claim2 = Claim(**sample_claim)
        claim2.text = "This is a factual claim about topic"
        claim2.attribution = "Different Source"
        
        groups = service._group_similar_claims([claim1, claim2])
        
        assert len(groups) == 1
        assert len(groups[0]) == 2
    
    def test_group_similar_claims_multiple_groups(self, service, sample_claim):
        """Test grouping creates multiple groups for different claims."""
        claim1 = Claim(**sample_claim)
        claim1.text = "First claim about topic A"
        
        claim2 = Claim(**sample_claim)
        claim2.text = "Second claim about topic B completely different"
        
        groups = service._group_similar_claims([claim1, claim2])
        
        assert len(groups) == 2
        assert len(groups[0]) == 1
        assert len(groups[1]) == 1
    
    def test_cross_corroborate_confirmed_claims(self, service, sample_claim):
        """Test cross-corroboration marks claims as confirmed."""
        claim1 = Claim(**sample_claim)
        claim1.text = "This is a fact"
        claim1.attribution = "Source A"
        
        claim2 = Claim(**sample_claim)
        claim2.text = "This is a fact"
        claim2.attribution = "Source B"
        claim2.article_url = "https://example.com/2"
        
        result = service.cross_corroborate([claim1, claim2])
        
        # Should have one confirmed claim
        confirmed = [c for c in result if c.is_confirmed]
        assert len(confirmed) > 0
        assert confirmed[0].corroboration_count == 2
    
    def test_cross_corroborate_uncorroborated_claims(self, service, sample_claim):
        """Test that single-source claims remain uncorroborated."""
        claim = Claim(**sample_claim)
        
        result = service.cross_corroborate([claim])
        
        assert len(result) == 1
        assert result[0].is_confirmed is False
        assert result[0].corroboration_count == 0
    
    @pytest.mark.asyncio
    async def test_generate_fact_ledger(self, service, sample_articles_list):
        """Test generating a complete fact ledger."""
        articles = [Article(**data) for data in sample_articles_list[:2]]
        
        with patch.object(service, 'extract_claims', new_callable=AsyncMock) as mock_extract:
            # Create claims with different states
            confirmed_claim = Claim(
                text="Confirmed claim",
                attribution="Source A",
                article_url="url1",
                is_confirmed=True,
                corroboration_count=2
            )
            
            uncorroborated_claim = Claim(
                text="Uncorroborated claim",
                attribution="Source B",
                article_url="url2"
            )
            
            with patch.object(service, 'cross_corroborate') as mock_corroborate:
                mock_corroborate.return_value = [confirmed_claim, uncorroborated_claim]
                mock_extract.return_value = []
                
                ledger = await service.generate_fact_ledger("story123", articles)
                
                assert isinstance(ledger, FactLedger)
                assert ledger.story_id == "story123"
                assert len(ledger.confirmed_claims) == 1
                assert len(ledger.uncorroborated_claims) == 1
                assert len(ledger.disputed_claims) == 0
    
    @pytest.mark.asyncio
    async def test_generate_fact_ledger_with_disputed(self, service, sample_articles_list):
        """Test fact ledger with disputed claims."""
        articles = [Article(**data) for data in sample_articles_list[:1]]
        
        with patch.object(service, 'extract_claims', new_callable=AsyncMock) as mock_extract:
            disputed_claim = Claim(
                text="Disputed claim",
                attribution="Source A",
                article_url="url1",
                is_disputed=True
            )
            
            with patch.object(service, 'cross_corroborate') as mock_corroborate:
                mock_corroborate.return_value = [disputed_claim]
                mock_extract.return_value = []
                
                ledger = await service.generate_fact_ledger("story123", articles)
                
                assert len(ledger.disputed_claims) == 1
