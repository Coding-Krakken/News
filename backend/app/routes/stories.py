from fastapi import APIRouter, HTTPException, Query, BackgroundTasks, Depends
from typing import List, Optional
from ..database import get_database
from ..models.schemas import Article, Story
from ..services.clustering import StoryClusteringService

router = APIRouter()
clustering_service = StoryClusteringService()

async def cluster_articles_background():
    """Background task to cluster articles into stories"""
    try:
        db = get_database()
        
        # Fetch all articles
        cursor = db.articles.find({}, {"_id": 0})
        articles_data = await cursor.to_list(length=1000)
        articles = [Article(**data) for data in articles_data]
        
        # Cluster articles
        stories = clustering_service.cluster_articles(articles)
        
        # Update articles with story IDs and save stories
        for story in stories:
            # Save story
            await db.stories.update_one(
                {"story_id": story.story_id},
                {"$set": story.model_dump()},
                upsert=True
            )
            
            # Update articles with story ID
            for article_url in story.article_ids:
                await db.articles.update_one(
                    {"url": article_url},
                    {"$set": {"story_id": story.story_id}}
                )
        
        print(f"Clustered {len(articles)} articles into {len(stories)} stories")
    except Exception as e:
        print(f"Error in background clustering: {str(e)}")

@router.post("/cluster", response_model=dict)
async def trigger_clustering(background_tasks: BackgroundTasks):
    """Trigger article clustering into stories"""
    background_tasks.add_task(cluster_articles_background)
    return {"message": "Clustering started in background"}

@router.get("/", response_model=List[dict])
async def get_stories(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db=Depends(get_database)
):
    """Get all stories"""
    try:
        cursor = db.stories.find({}, {"_id": 0}).sort("last_updated", -1).skip(skip).limit(limit)
        stories = await cursor.to_list(length=limit)
        
        return stories
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

from fastapi.encoders import jsonable_encoder

@router.get("/{story_id}", response_model=dict)
async def get_story(story_id: str, db=Depends(get_database)):
    """Get a specific story by ID"""
    story = await db.stories.find_one({"story_id": story_id}, {"_id": 0})
    if not story:
        raise HTTPException(status_code=404, detail="Story not found")
    return jsonable_encoder(story)

@router.get("/{story_id}/articles", response_model=List[dict])
async def get_story_articles(story_id: str, db=Depends(get_database)):
    """Get all articles in a story"""
    story = await db.stories.find_one({"story_id": story_id}, {"_id": 0})
    if not story:
        raise HTTPException(status_code=404, detail="Story not found")
    articles = await db.articles.find(
        {"url": {"$in": story["article_ids"]}}, {"_id": 0}
    ).to_list(length=100)
    return articles

@router.get("/{story_id}/coverage", response_model=dict)
async def get_story_coverage(story_id: str, db=Depends(get_database)):
    """Get coverage matrix for a story"""
    story = await db.stories.find_one({"story_id": story_id})
    if not story:
        raise HTTPException(status_code=404, detail="Story not found")
    all_sources = await db.articles.distinct("source_name")
    coverage = {source: source in story["sources_covered"] for source in all_sources}
    return {
        "story_id": story_id,
        "coverage": coverage,
        "sources_covered": story["sources_covered"],
        "total_sources": len(all_sources),
        "coverage_percentage": len(story["sources_covered"]) / len(all_sources) * 100 if all_sources else 0
    }
