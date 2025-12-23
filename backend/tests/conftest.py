import pytest
import asyncio
from typing import AsyncGenerator, Generator
from httpx import AsyncClient
from motor.motor_asyncio import AsyncIOMotorClient
from mongomock_motor import AsyncMongoMockClient
import os

# Set test environment
os.environ["MONGODB_URL"] = "mongodb://test"
# Use the production-like default DB name for tests so settings validation
# that expects `news_analytics` sees the same default value.
os.environ["DATABASE_NAME"] = "news_analytics"
# Use a realistic OpenAI-style test key (matches tests expecting `sk-test`).
os.environ["OPENAI_API_KEY"] = "sk-test"
# Inform application it's running under tests so integration points can adjust
os.environ["TESTING"] = "true"

from app.main import app
from app.database import get_database


@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
async def mock_db():
    """Provide a mock MongoDB database for testing."""
    client = AsyncMongoMockClient()
    # Use the same database name as the environment to keep tests consistent.
    db = client.news_analytics
    
    # Create indexes
    await db.articles.create_index("url", unique=True)
    await db.articles.create_index("published_date")
    await db.articles.create_index("source_name")
    await db.articles.create_index("category")
    await db.stories.create_index("story_id", unique=True)
    await db.stories.create_index("created_at")
    # Ensure users collection exists for auth tests
    await db.users.create_index("email", unique=True)
    
    yield db
    
    # Cleanup
    await client.drop_database("news_analytics")


@pytest.fixture
async def client(mock_db) -> AsyncGenerator[AsyncClient, None]:
    """Provide an async HTTP client for testing the API."""
    
    # Override get_database dependency
    def override_get_database():
        return mock_db
    
    app.dependency_overrides[get_database] = override_get_database
    # Also set the global database in the application module so code that
    # calls `get_database()` directly (instead of using Depends) uses the
    # mock DB during tests.
    import app.database as app_database
    app_database.database = mock_db
    
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac
    
    app.dependency_overrides.clear()


@pytest.fixture
def sample_article_data():
    """Provide sample article data for testing."""
    from datetime import datetime
    return {
        "url": "https://example.com/article1",
        "title": "Test Article Title",
        "content": "This is test article content with some information about a topic.",
        "summary": "This is test article content with some information",
        "source_name": "Test Source",
        "source_url": "https://example.com",
        "author": "Test Author",
        "published_date": datetime.utcnow(),
        "category": "technology",
        "geography": "United States",
        "ideology": "center",
        "tags": ["test", "article"],
        "embedding": None,
        "story_id": None,
    }


@pytest.fixture
def sample_articles_list(sample_article_data):
    """Provide a list of sample articles for testing."""
    from datetime import datetime, timedelta
    articles = []
    
    for i in range(5):
        article = sample_article_data.copy()
        article["url"] = f"https://example.com/article{i}"
        article["title"] = f"Test Article {i}"
        article["source_name"] = f"Source {i % 2}"  # Alternate between 2 sources
        article["published_date"] = datetime.utcnow() - timedelta(hours=i)
        articles.append(article)
    
    return articles


@pytest.fixture
def sample_story_data():
    """Provide sample story data for testing."""
    from datetime import datetime
    return {
        "story_id": "test_story_123",
        "title": "Test Story Title",
        "summary": "Test story summary",
        "article_ids": ["https://example.com/article1", "https://example.com/article2"],
        "sources_covered": ["Source A", "Source B"],
        "sources_not_covered": [],
        "category": "technology",
        "geographies": ["United States"],
        "ideologies": ["center"],
        "first_seen": datetime.utcnow(),
        "last_updated": datetime.utcnow(),
        "article_count": 2,
    }


@pytest.fixture
def sample_claim():
    """Provide sample claim data for testing."""
    return {
        "text": "This is a factual claim",
        "attribution": "Test Source",
        "article_url": "https://example.com/article1",
        "is_confirmed": False,
        "is_disputed": False,
        "supporting_sources": [],
        "disputing_sources": [],
        "corroboration_count": 0,
    }


@pytest.fixture
def mock_rss_feed():
    """Provide mock RSS feed data."""
    return """<?xml version="1.0" encoding="UTF-8"?>
    <rss version="2.0">
        <channel>
            <title>Test News Feed</title>
            <link>https://example.com</link>
            <description>Test feed description</description>
            <item>
                <title>Test News Article</title>
                <link>https://example.com/news1</link>
                <description>Test article description</description>
                <pubDate>Mon, 15 Dec 2025 12:00:00 GMT</pubDate>
                <author>Test Author</author>
            </item>
        </channel>
    </rss>"""


@pytest.fixture
def mock_openai_response():
    """Provide mock OpenAI API response."""
    return {
        "choices": [
            {
                "message": {
                    "content": '[{"text": "Test claim", "is_factual": true}]'
                }
            }
        ]
    }
