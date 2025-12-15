from sentence_transformers import SentenceTransformer
from sklearn.cluster import DBSCAN
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from typing import List, Dict
from datetime import datetime, timedelta
from ..models.schemas import Article, Story
import hashlib

class StoryClusteringService:
    """Service for clustering articles into story events"""
    
    def __init__(self):
        # Load sentence transformer model for embeddings
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.similarity_threshold = 0.7
        self.time_window_hours = 72  # Articles within 72 hours can be clustered
    
    def generate_embeddings(self, articles: List[Article]) -> List[Article]:
        """Generate embeddings for articles"""
        texts = [f"{article.title} {article.content}" for article in articles]
        embeddings = self.model.encode(texts)
        
        for i, article in enumerate(articles):
            article.embedding = embeddings[i].tolist()
        
        return articles
    
    def cluster_articles(self, articles: List[Article]) -> List[Story]:
        """Cluster articles into stories using DBSCAN"""
        if not articles:
            return []
        
        # Filter articles by time window
        current_time = datetime.utcnow()
        time_threshold = current_time - timedelta(hours=self.time_window_hours)
        recent_articles = [a for a in articles if a.published_date >= time_threshold]
        
        if not recent_articles:
            return []
        
        # Generate embeddings if not already present
        articles_without_embeddings = [a for a in recent_articles if not a.embedding]
        if articles_without_embeddings:
            self.generate_embeddings(articles_without_embeddings)
        
        # Extract embeddings
        embeddings = np.array([article.embedding for article in recent_articles])
        
        # Perform clustering using DBSCAN
        clustering = DBSCAN(
            eps=1 - self.similarity_threshold,
            min_samples=2,
            metric='cosine'
        ).fit(embeddings)
        
        # Group articles by cluster
        clusters: Dict[int, List[Article]] = {}
        for idx, label in enumerate(clustering.labels_):
            if label not in clusters:
                clusters[label] = []
            clusters[label].append(recent_articles[idx])
        
        # Create Story objects
        stories = []
        for cluster_id, cluster_articles in clusters.items():
            if cluster_id == -1:  # Skip noise points
                continue
            
            story = self._create_story_from_cluster(cluster_id, cluster_articles)
            stories.append(story)
        
        return stories
    
    def _create_story_from_cluster(self, cluster_id: int, articles: List[Article]) -> Story:
        """Create a Story object from a cluster of articles"""
        # Generate story ID
        article_urls = sorted([a.url for a in articles])
        story_id = hashlib.md5("".join(article_urls).encode()).hexdigest()[:16]
        
        # Use the most recent article's title as story title
        sorted_articles = sorted(articles, key=lambda x: x.published_date, reverse=True)
        title = sorted_articles[0].title
        
        # Create summary from most common content
        summary = sorted_articles[0].summary or sorted_articles[0].content[:200]
        
        # Collect metadata
        sources_covered = list(set([a.source_name for a in articles]))
        geographies = list(set([a.geography for a in articles if a.geography]))
        ideologies = list(set([a.ideology for a in articles if a.ideology]))
        category = articles[0].category
        
        # Get article IDs
        article_ids = [a.url for a in articles]
        
        # Timestamps
        first_seen = min([a.published_date for a in articles])
        last_updated = max([a.published_date for a in articles])
        
        story = Story(
            story_id=story_id,
            title=title,
            summary=summary,
            article_ids=article_ids,
            sources_covered=sources_covered,
            sources_not_covered=[],
            category=category,
            geographies=geographies,
            ideologies=ideologies,
            first_seen=first_seen,
            last_updated=last_updated,
            article_count=len(articles)
        )
        
        return story
    
    def calculate_similarity(self, article1: Article, article2: Article) -> float:
        """Calculate similarity between two articles"""
        if not article1.embedding or not article2.embedding:
            return 0.0
        
        emb1 = np.array(article1.embedding).reshape(1, -1)
        emb2 = np.array(article2.embedding).reshape(1, -1)
        
        similarity = cosine_similarity(emb1, emb2)[0][0]
        return float(similarity)
