from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class Article(BaseModel):
    """Article model"""
    url: str
    title: str
    content: str
    summary: Optional[str] = None
    source_name: str
    source_url: str
    author: Optional[str] = None
    published_date: datetime
    category: Optional[str] = None
    geography: Optional[str] = None
    ideology: Optional[str] = None  # left, center, right, etc.
    tags: List[str] = Field(default_factory=list)
    embedding: Optional[List[float]] = None
    story_id: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_schema_extra = {
            "example": {
                "url": "https://example.com/article",
                "title": "Breaking News Title",
                "content": "Full article content...",
                "source_name": "Example News",
                "source_url": "https://example.com",
                "published_date": "2024-01-01T12:00:00",
                "category": "politics",
                "geography": "United States",
                "ideology": "center"
            }
        }

class Story(BaseModel):
    """Story cluster model"""
    story_id: str
    title: str
    summary: str
    article_ids: List[str]
    sources_covered: List[str]
    sources_not_covered: List[str] = Field(default_factory=list)
    category: Optional[str] = None
    geographies: List[str] = Field(default_factory=list)
    ideologies: List[str] = Field(default_factory=list)
    first_seen: datetime
    last_updated: datetime
    article_count: int = 0
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_schema_extra = {
            "example": {
                "story_id": "story_123",
                "title": "Major Event Title",
                "summary": "Summary of the story...",
                "article_ids": ["article1", "article2"],
                "sources_covered": ["Source A", "Source B"],
                "category": "politics",
                "first_seen": "2024-01-01T12:00:00"
            }
        }

class Claim(BaseModel):
    """Individual claim model"""
    text: str
    attribution: str  # Which source made this claim
    article_url: str
    is_confirmed: bool = False
    is_disputed: bool = False
    supporting_sources: List[str] = Field(default_factory=list)
    disputing_sources: List[str] = Field(default_factory=list)
    corroboration_count: int = 0

class FactLedger(BaseModel):
    """Fact ledger for a story"""
    story_id: str
    confirmed_claims: List[Claim] = Field(default_factory=list)
    disputed_claims: List[Claim] = Field(default_factory=list)
    uncorroborated_claims: List[Claim] = Field(default_factory=list)
    generated_at: datetime = Field(default_factory=datetime.utcnow)

class CoverageStats(BaseModel):
    """Coverage statistics"""
    by_source: dict = Field(default_factory=dict)
    by_category: dict = Field(default_factory=dict)
    by_geography: dict = Field(default_factory=dict)
    by_ideology: dict = Field(default_factory=dict)
    by_time: dict = Field(default_factory=dict)
    total_articles: int = 0
    total_stories: int = 0
