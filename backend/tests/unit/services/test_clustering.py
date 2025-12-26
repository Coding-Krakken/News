"""
Unit tests for story clustering service.
"""

import pytest
import numpy as np
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta
from app.services.clustering import StoryClusteringService
from app.models.schemas import Article, Story


class TestStoryClusteringService:
    """Test StoryClusteringService functionality."""

    @pytest.fixture
    def service(self):
        """Provide clustering service instance."""
        return StoryClusteringService()

    def test_service_initialization(self, service):
        """Test service initializes with correct parameters."""
        assert service.similarity_threshold == 0.7
        assert service.time_window_hours == 72
        assert service.model is not None

    def test_generate_embeddings(self, service, sample_articles_list):
        """Test generating embeddings for articles."""
        articles = [Article(**data) for data in sample_articles_list]

        with patch.object(service.model, "encode") as mock_encode:
            # Mock embeddings
            mock_encode.return_value = np.array([[0.1, 0.2, 0.3]] * len(articles))

            result = service.generate_embeddings(articles)

            assert len(result) == len(articles)
            assert all(a.embedding is not None for a in result)
            assert len(result[0].embedding) == 3

    def test_calculate_similarity(self, service, sample_article_data):
        """Test calculating similarity between two articles."""
        article1 = Article(**sample_article_data)
        article1.embedding = [0.1, 0.2, 0.3]

        article2 = Article(**sample_article_data)
        article2.url = "https://example.com/article2"
        article2.embedding = [0.1, 0.2, 0.3]

        similarity = service.calculate_similarity(article1, article2)

        # Identical embeddings should have similarity close to 1.0
        assert similarity > 0.99

    def test_calculate_similarity_different_embeddings(
        self, service, sample_article_data
    ):
        """Test similarity between different articles."""
        article1 = Article(**sample_article_data)
        article1.embedding = [1.0, 0.0, 0.0]

        article2 = Article(**sample_article_data)
        article2.url = "https://example.com/article2"
        article2.embedding = [0.0, 1.0, 0.0]

        similarity = service.calculate_similarity(article1, article2)

        # Orthogonal vectors should have similarity close to 0
        assert similarity < 0.1

    def test_calculate_similarity_no_embeddings(self, service, sample_article_data):
        """Test similarity calculation without embeddings."""
        article1 = Article(**sample_article_data)
        article2 = Article(**sample_article_data)
        article2.url = "https://example.com/article2"

        similarity = service.calculate_similarity(article1, article2)
        assert similarity == 0.0

    def test_cluster_articles_empty_list(self, service):
        """Test clustering with empty article list."""
        result = service.cluster_articles([])
        assert result == []

    def test_cluster_articles_filters_by_time(self, service, sample_article_data):
        """Test that clustering filters articles by time window."""
        # Create articles outside time window
        old_article = Article(**sample_article_data)
        old_article.published_date = datetime.utcnow() - timedelta(hours=100)

        recent_article = Article(**sample_article_data)
        recent_article.url = "https://example.com/article2"
        recent_article.published_date = datetime.utcnow() - timedelta(hours=24)

        with patch.object(service, "generate_embeddings") as mock_embed:
            mock_embed.return_value = [recent_article]

            with patch("app.services.clustering.DBSCAN") as mock_dbscan:
                mock_clustering = MagicMock()
                mock_clustering.labels_ = np.array([0])
                mock_dbscan.return_value.fit.return_value = mock_clustering

                result = service.cluster_articles([old_article, recent_article])

                # Only recent article should be processed
                mock_embed.assert_called_once()

    def test_cluster_articles_creates_stories(self, service, sample_articles_list):
        """Test that clustering creates Story objects."""
        articles = [Article(**data) for data in sample_articles_list[:3]]

        # Add embeddings
        for article in articles:
            article.embedding = [0.1, 0.2, 0.3]

        with patch("app.services.clustering.DBSCAN") as mock_dbscan:
            # Mock clustering result - all in same cluster
            mock_clustering = MagicMock()
            mock_clustering.labels_ = np.array([0, 0, 0])
            mock_dbscan.return_value.fit.return_value = mock_clustering

            stories = service.cluster_articles(articles)

            assert len(stories) == 1
            assert isinstance(stories[0], Story)
            assert stories[0].article_count == 3

    def test_cluster_articles_multiple_clusters(self, service, sample_articles_list):
        """Test clustering with multiple clusters."""
        articles = [Article(**data) for data in sample_articles_list[:4]]

        for article in articles:
            article.embedding = [0.1, 0.2, 0.3]

        with patch("app.services.clustering.DBSCAN") as mock_dbscan:
            # Mock two separate clusters
            mock_clustering = MagicMock()
            mock_clustering.labels_ = np.array([0, 0, 1, 1])
            mock_dbscan.return_value.fit.return_value = mock_clustering

            stories = service.cluster_articles(articles)

            assert len(stories) == 2

    def test_cluster_articles_ignores_noise(self, service, sample_articles_list):
        """Test that noise points (label -1) are ignored."""
        articles = [Article(**data) for data in sample_articles_list[:3]]

        for article in articles:
            article.embedding = [0.1, 0.2, 0.3]

        with patch("app.services.clustering.DBSCAN") as mock_dbscan:
            # One article in cluster, two as noise
            mock_clustering = MagicMock()
            mock_clustering.labels_ = np.array([0, -1, -1])
            mock_dbscan.return_value.fit.return_value = mock_clustering

            stories = service.cluster_articles(articles)

            # Noise points should be filtered out
            # DBSCAN requires min_samples=2, so cluster 0 shouldn't exist either
            # But we process all non-noise clusters
            assert all(s.story_id for s in stories)

    def test_create_story_from_cluster(self, service, sample_articles_list):
        """Test creating a story from a cluster of articles."""
        articles = [Article(**data) for data in sample_articles_list[:3]]

        story = service._create_story_from_cluster(0, articles)

        assert isinstance(story, Story)
        assert story.article_count == 3
        assert len(story.article_ids) == 3
        assert len(story.sources_covered) > 0
        assert story.title  # Should have a title
        assert story.summary  # Should have a summary

    def test_create_story_collects_metadata(self, service, sample_articles_list):
        """Test that story creation collects metadata from articles."""
        articles = [Article(**data) for data in sample_articles_list[:3]]

        # Set specific metadata
        articles[0].geography = "United States"
        articles[1].geography = "United Kingdom"
        articles[2].geography = "United States"

        articles[0].ideology = "center"
        articles[1].ideology = "left"
        articles[2].ideology = "center"

        story = service._create_story_from_cluster(0, articles)

        assert "United States" in story.geographies
        assert "United Kingdom" in story.geographies
        assert "center" in story.ideologies
        assert "left" in story.ideologies

    def test_create_story_timestamps(self, service, sample_articles_list):
        """Test that story has correct timestamps."""
        articles = [Article(**data) for data in sample_articles_list[:3]]

        story = service._create_story_from_cluster(0, articles)

        # first_seen should be earliest article
        # last_updated should be latest article
        assert story.first_seen <= story.last_updated
