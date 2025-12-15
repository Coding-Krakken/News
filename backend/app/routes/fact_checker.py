from fastapi import APIRouter, HTTPException
from ..database import get_database
from ..models.schemas import Article, FactLedger
from ..services.fact_checker import FactCheckingService

router = APIRouter()
fact_checker = FactCheckingService()

@router.post("/{story_id}", response_model=FactLedger)
async def generate_fact_ledger(story_id: str):
    """Generate AI-powered fact ledger for a story"""
    try:
        db = get_database()
        
        # Get story
        story = await db.stories.find_one({"story_id": story_id})
        if not story:
            raise HTTPException(status_code=404, detail="Story not found")
        
        # Get all articles in the story
        articles_data = await db.articles.find(
            {"url": {"$in": story["article_ids"]}}
        ).to_list(length=100)
        
        articles = [Article(**data) for data in articles_data]
        
        # Generate fact ledger
        ledger = await fact_checker.generate_fact_ledger(story_id, articles)
        
        # Save fact ledger
        await db.fact_ledgers.update_one(
            {"story_id": story_id},
            {"$set": ledger.model_dump()},
            upsert=True
        )
        
        return ledger
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{story_id}", response_model=dict)
async def get_fact_ledger(story_id: str):
    """Get existing fact ledger for a story"""
    try:
        db = get_database()
        
        ledger = await db.fact_ledgers.find_one({"story_id": story_id})
        
        if not ledger:
            raise HTTPException(
                status_code=404,
                detail="Fact ledger not found. Generate one first using POST endpoint."
            )
        
        return ledger
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
