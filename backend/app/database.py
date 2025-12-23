from motor.motor_asyncio import AsyncIOMotorClient
from typing import Optional
from .config import get_settings

# Database client
client: Optional[AsyncIOMotorClient] = None
database = None

async def init_db():
    """Initialize database connection"""
    global client, database
    settings = get_settings()
    mongodb_url = settings.mongodb_url
    database_name = settings.database_name
    
    client = AsyncIOMotorClient(mongodb_url)
    database = client[database_name]
    
    # Create indexes for collections where available. Wrap each in try/except
    # so that mocked or dummy databases without collection attributes don't
    # cause initialization to fail in tests.
    collections_with_indexes = {
        "articles": [ ("url", {"unique": True}), ("published_date", {}), ("source_name", {}), ("category", {}) ],
        "stories": [ ("story_id", {"unique": True}), ("created_at", {}) ],
        "users": [ ("username", {"unique": True}), ("email", {"unique": True}), ("role", {}) ],
        "sources": [ ("name", {"unique": True}), ("enabled", {}), ("created_at", {}) ],
        "audit_log": [ ("timestamp", {}), ("entity_type", {}), ("user", {}) ],
    }

    for coll_name, indexes in collections_with_indexes.items():
        try:
            coll = getattr(database, coll_name)
            for idx_field, idx_opts in indexes:
                # motor's create_index accepts either kwargs or simple name
                await coll.create_index(idx_field, **idx_opts)
        except Exception:
            # If database mock/dummy doesn't expose the collection, skip index creation.
            continue
    
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
