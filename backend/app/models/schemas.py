from pydantic import BaseModel, Field, EmailStr, validator
from typing import Optional, List
from datetime import datetime
from enum import Enum


class UserRole(str, Enum):
    """User role enumeration"""
    USER = "user"
    ADMIN = "admin"


class User(BaseModel):
    """User model"""
    username: str
    email: EmailStr
    full_name: Optional[str] = None
    disabled: bool = False
    role: UserRole = UserRole.USER
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # User preferences
    bookmarked_stories: List[str] = Field(default_factory=list)
    bookmarked_articles: List[str] = Field(default_factory=list)
    saved_filters: dict = Field(default_factory=dict)
    notification_preferences: dict = Field(default_factory=dict)
    
    class Config:
        json_schema_extra = {
            "example": {
                "username": "johndoe",
                "email": "john@example.com",
                "full_name": "John Doe",
                "role": "user"
            }
        }


class UserInDB(User):
    """User model with hashed password for database storage"""
    hashed_password: str


class UserCreate(BaseModel):
    """Schema for user registration"""
    username: str
    email: EmailStr
    password: str
    full_name: Optional[str] = None
    
    @validator('username')
    def username_alphanumeric(cls, v: str) -> str:
        if not v.isalnum():
            raise ValueError('Username must be alphanumeric')
        if len(v) < 3:
            raise ValueError('Username must be at least 3 characters')
        return v
    
    @validator('password')
    def password_strength(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters')
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(c.islower() for c in v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one digit')
        return v


class UserUpdate(BaseModel):
    """Schema for user profile updates"""
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    notification_preferences: Optional[dict] = None


class Token(BaseModel):
    """JWT token response"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Data stored in JWT token"""
    username: Optional[str] = None
    role: Optional[str] = None


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
