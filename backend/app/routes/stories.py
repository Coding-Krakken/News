from fastapi import APIRouter, HTTPException, Query, BackgroundTasks
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
        cursor = db.articles.find({})
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
    limit: int = Query(20, ge=1, le=100)
):
    """Get all stories"""
    try:
        db = get_database()
        cursor = db.stories.find({}).sort("last_updated", -1).skip(skip).limit(limit)
        stories = await cursor.to_list(length=limit)
        
        return stories
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{story_id}", response_model=dict)
async def get_story(story_id: str):
    """Get a specific story by ID"""
    try:
        db = get_database()
        story = await db.stories.find_one({"story_id": story_id})
        
        if not story:
            raise HTTPException(status_code=404, detail="Story not found")
        
        return story
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{story_id}/articles", response_model=List[dict])
async def get_story_articles(story_id: str):
    """Get all articles in a story"""
    try:
        db = get_database()
        
        # Get story
        story = await db.stories.find_one({"story_id": story_id})
        if not story:
            raise HTTPException(status_code=404, detail="Story not found")
        
        # Get articles
        articles = await db.articles.find(
            {"url": {"$in": story["article_ids"]}}
        ).to_list(length=100)
        
        return articles
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{story_id}/coverage", response_model=dict)
async def get_story_coverage(story_id: str):
    """Get coverage matrix for a story"""
    try:
        db = get_database()
        
        # Get story
        story = await db.stories.find_one({"story_id": story_id})
        if not story:
            raise HTTPException(status_code=404, detail="Story not found")
        
        # Get all sources
        all_sources = await db.articles.distinct("source_name")
        
        # Build coverage matrix
        coverage = {}
        for source in all_sources:
            coverage[source] = source in story["sources_covered"]
        
        return {
            "story_id": story_id,
            "coverage": coverage,
            "sources_covered": story["sources_covered"],
            "total_sources": len(all_sources),
            "coverage_percentage": len(story["sources_covered"]) / len(all_sources) * 100 if all_sources else 0
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
