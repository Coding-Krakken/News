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
        """Parse RSS feed entry into Article, robust to mocks and missing fields."""
        try:
            # Extract published date
            published_date = datetime.utcnow()
            if hasattr(entry, 'published_parsed') and getattr(entry, 'published_parsed', None):
                try:
                    published_date = datetime(*getattr(entry, 'published_parsed')[:6])
                except Exception:
                    pass

            # Extract content
            content = ""
            summary_val = getattr(entry, 'summary', None)
            description_val = getattr(entry, 'description', None)
            if summary_val:
                try:
                    content = BeautifulSoup(str(summary_val), 'html.parser').get_text()
                except Exception:
                    content = str(summary_val)
            elif description_val:
                try:
                    content = BeautifulSoup(str(description_val), 'html.parser').get_text()
                except Exception:
                    content = str(description_val)

            # Extract category
            category = None
            tags_val = getattr(entry, 'tags', None)
            if tags_val and isinstance(tags_val, (list, tuple)) and len(tags_val) > 0:
                tag0 = tags_val[0]
                # tag0 may be a Mock or object with .term
                category = getattr(tag0, 'term', None)

            # Extract author
            author = getattr(entry, 'author', None)
            if author is not None and not isinstance(author, str):
                # If author is a Mock or not a string, skip
                author = None

            # Required fields: url, title
            url = getattr(entry, 'link', None)
            title = getattr(entry, 'title', None)
            if not url or not title:
                return None

            article = Article(
                url=url,
                title=title,
                content=content,
                summary=content[:200] if content else None,
                source_name=source["name"],
                source_url=source["url"],
                author=author,
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
