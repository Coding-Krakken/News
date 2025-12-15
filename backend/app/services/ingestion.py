import feedparser
import aiohttp
from bs4 import BeautifulSoup
from datetime import datetime
from typing import List, Dict, Optional
from ..models.schemas import Article
import hashlib

class NewsIngestionService:
    """Service for ingesting news from various sources"""
    
    def __init__(self):
        self.sources = [
            {
                "name": "BBC News",
                "url": "http://feeds.bbci.co.uk/news/rss.xml",
                "type": "rss",
                "ideology": "center",
                "geography": "United Kingdom"
            },
            {
                "name": "CNN",
                "url": "http://rss.cnn.com/rss/cnn_topstories.rss",
                "type": "rss",
                "ideology": "center-left",
                "geography": "United States"
            },
            {
                "name": "Reuters",
                "url": "https://www.reutersagency.com/feed/",
                "type": "rss",
                "ideology": "center",
                "geography": "International"
            },
            {
                "name": "The Guardian",
                "url": "https://www.theguardian.com/world/rss",
                "type": "rss",
                "ideology": "center-left",
                "geography": "United Kingdom"
            },
        ]
    
    async def ingest_from_rss(self, source: Dict) -> List[Article]:
        """Ingest articles from RSS feed"""
        articles = []
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(source["url"], timeout=aiohttp.ClientTimeout(total=30)) as response:
                    if response.status == 200:
                        content = await response.text()
                        feed = feedparser.parse(content)
                        
                        for entry in feed.entries[:10]:  # Limit to 10 articles per source
                            article = self._parse_rss_entry(entry, source)
                            if article:
                                articles.append(article)
        except Exception as e:
            print(f"Error ingesting from {source['name']}: {str(e)}")
        
        return articles
    
    def _parse_rss_entry(self, entry, source: Dict) -> Optional[Article]:
        """Parse RSS feed entry into Article"""
        try:
            # Extract published date
            published_date = datetime.utcnow()
            if hasattr(entry, 'published_parsed') and entry.published_parsed:
                published_date = datetime(*entry.published_parsed[:6])
            
            # Extract content
            content = ""
            if hasattr(entry, 'summary'):
                content = BeautifulSoup(entry.summary, 'html.parser').get_text()
            elif hasattr(entry, 'description'):
                content = BeautifulSoup(entry.description, 'html.parser').get_text()
            
            # Extract category
            category = None
            if hasattr(entry, 'tags') and entry.tags:
                category = entry.tags[0].term if entry.tags else None
            
            article = Article(
                url=entry.link,
                title=entry.title,
                content=content,
                summary=content[:200] if content else None,
                source_name=source["name"],
                source_url=source["url"],
                author=entry.author if hasattr(entry, 'author') else None,
                published_date=published_date,
                category=category,
                geography=source.get("geography"),
                ideology=source.get("ideology"),
                tags=[]
            )
            
            return article
        except Exception as e:
            print(f"Error parsing entry: {str(e)}")
            return None
    
    async def ingest_all_sources(self) -> List[Article]:
        """Ingest articles from all configured sources"""
        all_articles = []
        
        for source in self.sources:
            if source["type"] == "rss":
                articles = await self.ingest_from_rss(source)
                all_articles.extend(articles)
        
        return all_articles
    
    def add_source(self, name: str, url: str, source_type: str, ideology: str, geography: str):
        """Add a new news source"""
        self.sources.append({
            "name": name,
            "url": url,
            "type": source_type,
            "ideology": ideology,
            "geography": geography
        })
    
    def get_sources(self) -> List[Dict]:
        """Get all configured sources"""
        return self.sources
