from fastapi import APIRouter, HTTPException, Query, Depends
from typing import List, Optional
from datetime import datetime
from ..database import get_database
from ..models.schemas import Article, Story, CoverageStats
from ..services.analytics import AnalyticsService

router = APIRouter()
analytics_service = AnalyticsService()

@router.get("/stats", response_model=CoverageStats)
async def get_coverage_stats(db=Depends(get_database)):
    """Get comprehensive coverage statistics"""
    try:
        
        # Fetch all articles and stories
        articles_data = await db.articles.find({}, {"_id": 0}).to_list(length=10000)
        stories_data = await db.stories.find({}, {"_id": 0}).to_list(length=1000)
        
        articles = [Article(**data) for data in articles_data]
        stories = [Story(**data) for data in stories_data]
        
        stats = analytics_service.compute_coverage_stats(articles, stories)
        
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/filter", response_model=List[dict])
async def filter_articles(
    sources: Optional[str] = Query(None, description="Comma-separated list of sources"),
    categories: Optional[str] = Query(None, description="Comma-separated list of categories"),
    geographies: Optional[str] = Query(None, description="Comma-separated list of geographies"),
    ideologies: Optional[str] = Query(None, description="Comma-separated list of ideologies"),
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db=Depends(get_database)
):
    """Filter articles based on multiple criteria"""
    try:
        # Build MongoDB query
        query = {}
        if sources:
            query["source_name"] = {"$in": sources.split(",")}
        if categories:
            query["category"] = {"$in": categories.split(",")}
        if geographies:
            query["geography"] = {"$in": geographies.split(",")}
        if ideologies:
            query["ideology"] = {"$in": ideologies.split(",")}
        if start_date:
            if "published_date" not in query:
                query["published_date"] = {}
            query["published_date"]["$gte"] = datetime.fromisoformat(start_date)
        if end_date:
            if "published_date" not in query:
                query["published_date"] = {}
            query["published_date"]["$lte"] = datetime.fromisoformat(end_date)
        # Fetch filtered articles
        cursor = db.articles.find(query, {"_id": 0}).sort("published_date", -1).skip(skip).limit(limit)
        articles = await cursor.to_list(length=limit)
        return articles
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/facets", response_model=dict)
async def get_filter_facets(db=Depends(get_database)):
    """Get available filter options (facets)"""
    try:
        sources = await db.articles.distinct("source_name")
        categories = await db.articles.distinct("category")
        geographies = await db.articles.distinct("geography")
        ideologies = await db.articles.distinct("ideology")
        # Ensure all are lists of strings
        return {
            "sources": [str(s) for s in sources if s],
            "categories": [str(c) for c in categories if c],
            "geographies": [str(g) for g in geographies if g],
            "ideologies": [str(i) for i in ideologies if i]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
