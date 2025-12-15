"""
End-to-end tests for the complete workflow.
"""
import pytest
from httpx import AsyncClient
from unittest.mock import patch, AsyncMock, MagicMock
import numpy as np


@pytest.mark.e2e
class TestCompleteWorkflow:
    """End-to-end tests for complete news analytics workflow."""
    
    @pytest.mark.asyncio
    async def test_complete_workflow(self, client: AsyncClient, mock_db):
        """Test complete workflow from ingestion to fact-checking."""
        
        # Step 1: Check initial state
        response = await client.get("/api/articles/sources/list")
        assert response.status_code == 200
        sources = response.json()
        assert len(sources) > 0
        
        # Step 2: Get stats (should be empty)
        response = await client.get("/api/analytics/stats")
        assert response.status_code == 200
        stats = response.json()
        assert stats["total_articles"] == 0
        
        # Step 3: Manually insert articles (simulating ingestion)
        from datetime import datetime
        articles_data = [
            {
                "url": f"https://example.com/article{i}",
                "title": f"Test Article {i}",
                "content": "This is a test article with some content about important events.",
                "source_name": f"Source {i % 2}",
                "source_url": "https://example.com",
                "published_date": datetime.utcnow(),
                "category": "technology",
                "geography": "United States",
                "ideology": "center",
                "embedding": [0.1 + i*0.01, 0.2 + i*0.01, 0.3 + i*0.01]
            }
            for i in range(4)
        ]
        
        for article_data in articles_data:
            await mock_db.articles.insert_one(article_data)
        
        # Step 4: Check articles were inserted
        response = await client.get("/api/articles/")
        assert response.status_code == 200
        articles = response.json()
        assert len(articles) == 4
        
        # Step 5: Trigger clustering
        with patch('app.services.clustering.DBSCAN') as mock_dbscan:
            mock_clustering = MagicMock()
            mock_clustering.labels_ = np.array([0, 0, 1, 1])
            mock_dbscan.return_value.fit.return_value = mock_clustering
            
            response = await client.post("/api/stories/cluster")
            assert response.status_code == 200
        
        # Step 6: Get stories
        response = await client.get("/api/stories/")
        assert response.status_code == 200
        # Note: Stories might not be immediately available due to background processing
        
        # Step 7: Get analytics
        response = await client.get("/api/analytics/stats")
        assert response.status_code == 200
        stats = response.json()
        assert stats["total_articles"] == 4
        
        # Step 8: Get facets
        response = await client.get("/api/analytics/facets")
        assert response.status_code == 200
        facets = response.json()
        assert "Source 0" in facets["sources"]
        assert "Source 1" in facets["sources"]
        
        # Step 9: Filter articles
        response = await client.get("/api/analytics/filter?sources=Source 0")
        assert response.status_code == 200
        filtered = response.json()
        assert len(filtered) == 2
    
    @pytest.mark.asyncio
    async def test_fact_checking_workflow(self, client: AsyncClient, mock_db, sample_story_data, sample_articles_list):
        """Test fact-checking workflow."""
        
        # Insert story
        await mock_db.stories.insert_one(sample_story_data)
        
        # Insert articles for the story
        for i, article_url in enumerate(sample_story_data["article_ids"]):
            article_data = sample_articles_list[i].copy()
            article_data["url"] = article_url
            await mock_db.articles.insert_one(article_data)
        
        # Mock fact checker
        with patch('app.routes.fact_checker.fact_checker.generate_fact_ledger', new_callable=AsyncMock) as mock_generate:
            from app.models.schemas import FactLedger, Claim
            
            mock_ledger = FactLedger(
                story_id=sample_story_data["story_id"],
                confirmed_claims=[
                    Claim(
                        text="Confirmed fact from multiple sources",
                        attribution="Source A",
                        article_url=sample_story_data["article_ids"][0],
                        is_confirmed=True,
                        supporting_sources=["Source A", "Source B"],
                        corroboration_count=2
                    )
                ],
                disputed_claims=[],
                uncorroborated_claims=[
                    Claim(
                        text="Uncorroborated claim from single source",
                        attribution="Source A",
                        article_url=sample_story_data["article_ids"][0]
                    )
                ]
            )
            mock_generate.return_value = mock_ledger
            
            # Generate fact ledger
            response = await client.post(f"/api/fact-checker/{sample_story_data['story_id']}")
            assert response.status_code == 200
            ledger = response.json()
            
            assert len(ledger["confirmed_claims"]) == 1
            assert len(ledger["uncorroborated_claims"]) == 1
            assert ledger["confirmed_claims"][0]["is_confirmed"] is True
        
        # Retrieve the fact ledger
        response = await client.get(f"/api/fact-checker/{sample_story_data['story_id']}")
        assert response.status_code == 200
    
    @pytest.mark.asyncio
    async def test_coverage_matrix_workflow(self, client: AsyncClient, mock_db, sample_story_data, sample_articles_list):
        """Test coverage matrix workflow."""
        
        # Insert story
        await mock_db.stories.insert_one(sample_story_data)
        
        # Insert various articles to create sources
        for i, article_data in enumerate(sample_articles_list[:4]):
            article_data["source_name"] = f"Source {chr(65 + i)}"  # A, B, C, D
            await mock_db.articles.insert_one(article_data)
        
        # Get coverage matrix
        response = await client.get(f"/api/stories/{sample_story_data['story_id']}/coverage")
        assert response.status_code == 200
        coverage = response.json()
        
        assert "coverage" in coverage
        assert "sources_covered" in coverage
        assert "coverage_percentage" in coverage
        
        # Verify coverage matrix structure
        assert isinstance(coverage["coverage"], dict)
        assert coverage["coverage_percentage"] >= 0
        assert coverage["coverage_percentage"] <= 100
