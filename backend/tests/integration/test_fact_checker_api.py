"""
Integration tests for fact-checker API endpoints.
"""
import pytest
from httpx import AsyncClient
from unittest.mock import patch, AsyncMock


@pytest.mark.integration
class TestFactCheckerAPI:
    """Integration tests for fact-checker endpoints."""
    
    @pytest.mark.asyncio
    async def test_get_fact_ledger_not_found(self, client: AsyncClient, mock_db):
        """Test getting non-existent fact ledger."""
        response = await client.get("/api/fact-checker/nonexistent_story")
        
        assert response.status_code == 404
    
    @pytest.mark.asyncio
    async def test_get_fact_ledger_exists(self, client: AsyncClient, mock_db):
        """Test getting existing fact ledger."""
        # Insert a fact ledger
        from datetime import datetime
        ledger_data = {
            "story_id": "test_story",
            "confirmed_claims": [],
            "disputed_claims": [],
            "uncorroborated_claims": [],
            "generated_at": datetime.utcnow()
        }
        await mock_db.fact_ledgers.insert_one(ledger_data)
        
        response = await client.get("/api/fact-checker/test_story")
        
        assert response.status_code == 200
        data = response.json()
        assert data["story_id"] == "test_story"
    
    @pytest.mark.asyncio
    async def test_generate_fact_ledger_story_not_found(self, client: AsyncClient, mock_db):
        """Test generating fact ledger for non-existent story."""
        response = await client.post("/api/fact-checker/nonexistent_story")
        
        assert response.status_code == 404
    
    @pytest.mark.asyncio
    async def test_generate_fact_ledger_success(self, client: AsyncClient, mock_db, sample_story_data, sample_articles_list):
        """Test successfully generating a fact ledger."""
        # Insert story
        await mock_db.stories.insert_one(sample_story_data)
        
        # Insert articles for the story
        for i, article_url in enumerate(sample_story_data["article_ids"]):
            article_data = sample_articles_list[i].copy()
            article_data["url"] = article_url
            await mock_db.articles.insert_one(article_data)
        
        # Mock the fact checker service
        with patch('app.routes.fact_checker.fact_checker.generate_fact_ledger', new_callable=AsyncMock) as mock_generate:
            from app.models.schemas import FactLedger, Claim
            
            mock_ledger = FactLedger(
                story_id=sample_story_data["story_id"],
                confirmed_claims=[
                    Claim(
                        text="Test confirmed claim",
                        attribution="Source A",
                        article_url="url1",
                        is_confirmed=True
                    )
                ],
                disputed_claims=[],
                uncorroborated_claims=[]
            )
            mock_generate.return_value = mock_ledger
            
            response = await client.post(f"/api/fact-checker/{sample_story_data['story_id']}")
            
            assert response.status_code == 200
            data = response.json()
            assert data["story_id"] == sample_story_data["story_id"]
            assert "confirmed_claims" in data
            assert "disputed_claims" in data
            assert "uncorroborated_claims" in data
