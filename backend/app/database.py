from motor.motor_asyncio import AsyncIOMotorClient
from typing import Optional
import os
from dotenv import load_dotenv

load_dotenv()

# Database client
client: Optional[AsyncIOMotorClient] = None
database = None

async def init_db():
    """Initialize database connection"""
    global client, database
    mongodb_url = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
    database_name = os.getenv("DATABASE_NAME", "news_analytics")
    
    client = AsyncIOMotorClient(mongodb_url)
    database = client[database_name]
    
    # Create indexes for articles
    await database.articles.create_index("url", unique=True)
    await database.articles.create_index("published_date")
    await database.articles.create_index("source_name")
    await database.articles.create_index("category")
    
    # Create indexes for stories
    await database.stories.create_index("story_id", unique=True)
    await database.stories.create_index("created_at")
    
    # Create indexes for users
    await database.users.create_index("username", unique=True)
    await database.users.create_index("email", unique=True)
    await database.users.create_index("role")
    
    print(f"Connected to MongoDB: {database_name}")

async def close_db():
    """Close database connection"""
    global client
    if client:
        client.close()
        print("Disconnected from MongoDB")

def get_database():
    """Get database instance"""
    return database
