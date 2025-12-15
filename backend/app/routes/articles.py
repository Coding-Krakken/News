from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from datetime import datetime
from ..database import get_database
from ..models.schemas import Article
from ..services.ingestion import NewsIngestionService

router = APIRouter()
ingestion_service = NewsIngestionService()

@router.post("/ingest", response_model=dict)
async def ingest_articles():
    """Ingest articles from all configured sources"""
    try:
        articles = await ingestion_service.ingest_all_sources()
        
        db = get_database()
        inserted_count = 0
        
        for article in articles:
            try:
                # Insert article into database
                await db.articles.update_one(
                    {"url": article.url},
                    {"$set": article.model_dump()},
                    upsert=True
                )
                inserted_count += 1
            except Exception as e:
                print(f"Error inserting article: {str(e)}")
        
        return {
            "message": "Articles ingested successfully",
            "total_ingested": inserted_count,
            "total_sources": len(ingestion_service.get_sources())
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/", response_model=List[dict])
async def get_articles(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    source: Optional[str] = None,
    category: Optional[str] = None
):
    """Get articles with optional filtering"""
    try:
        db = get_database()
        
        # Build query
        query = {}
        if source:
            query["source_name"] = source
        if category:
            query["category"] = category
        
        # Fetch articles
        cursor = db.articles.find(query).sort("published_date", -1).skip(skip).limit(limit)
        articles = await cursor.to_list(length=limit)
        
        return articles
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{article_url:path}", response_model=dict)
async def get_article(article_url: str):
    """Get a specific article by URL"""
    try:
        db = get_database()
        article = await db.articles.find_one({"url": article_url})
        
        if not article:
            raise HTTPException(status_code=404, detail="Article not found")
        
        return article
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/sources/list", response_model=List[dict])
async def get_sources():
    """Get all configured news sources"""
    return ingestion_service.get_sources()

@router.post("/sources/add", response_model=dict)
async def add_source(
    name: str,
    url: str,
    source_type: str = "rss",
    ideology: str = "center",
    geography: str = "International"
):
    """Add a new news source"""
    try:
        ingestion_service.add_source(name, url, source_type, ideology, geography)
        return {"message": f"Source '{name}' added successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
