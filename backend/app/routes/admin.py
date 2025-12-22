"""
Admin dashboard routes for source management and moderation.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from datetime import datetime

from ..database import get_database
from ..models.schemas import User
from ..utils.dependencies import get_current_admin_user

router = APIRouter()


# Source Management Models
from pydantic import BaseModel, HttpUrl


class NewsSource(BaseModel):
    """News source model for admin management."""
    name: str
    url: HttpUrl
    source_type: str = "rss"  # rss, api, scraper
    ideology: str = "center"  # left, center-left, center, center-right, right
    geography: str = "International"
    category: Optional[str] = None
    enabled: bool = True
    quality_score: Optional[float] = None
    reliability_score: Optional[float] = None
    bias_score: Optional[float] = None
    created_at: datetime = None
    updated_at: datetime = None
    created_by: Optional[str] = None
    moderation_notes: Optional[str] = None


class NewsSourceCreate(BaseModel):
    """Schema for creating a news source."""
    name: str
    url: HttpUrl
    source_type: str = "rss"
    ideology: str = "center"
    geography: str = "International"
    category: Optional[str] = None


class NewsSourceUpdate(BaseModel):
    """Schema for updating a news source."""
    name: Optional[str] = None
    url: Optional[HttpUrl] = None
    source_type: Optional[str] = None
    ideology: Optional[str] = None
    geography: Optional[str] = None
    category: Optional[str] = None
    enabled: Optional[bool] = None
    moderation_notes: Optional[str] = None


class AuditLog(BaseModel):
    """Audit log entry model."""
    action: str
    entity_type: str
    entity_id: str
    user: str
    timestamp: datetime
    details: dict
    ip_address: Optional[str] = None


# Source Management Endpoints

@router.get("/sources", response_model=List[NewsSource])
async def list_sources(
    skip: int = 0,
    limit: int = 100,
    enabled_only: bool = False,
    current_user: User = Depends(get_current_admin_user)
):
    """List all news sources (admin only)."""
    db = get_database()
    
    query = {}
    if enabled_only:
        query["enabled"] = True
    
    cursor = db.sources.find(query).skip(skip).limit(limit)
    sources = await cursor.to_list(length=limit)
    
    # Remove MongoDB _id
    for source in sources:
        source.pop("_id", None)
    
    return [NewsSource(**source) for source in sources]


@router.get("/sources/{source_id}", response_model=NewsSource)
async def get_source(
    source_id: str,
    current_user: User = Depends(get_current_admin_user)
):
    """Get a specific news source (admin only)."""
    db = get_database()
    
    source = await db.sources.find_one({"name": source_id})
    if not source:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Source not found"
        )
    
    source.pop("_id", None)
    return NewsSource(**source)


@router.post("/sources", response_model=NewsSource, status_code=status.HTTP_201_CREATED)
async def create_source(
    source_data: NewsSourceCreate,
    current_user: User = Depends(get_current_admin_user)
):
    """Create a new news source (admin only)."""
    db = get_database()
    
    # Check if source already exists
    existing = await db.sources.find_one({"name": source_data.name})
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Source with this name already exists"
        )
    
    # Create source
    source_dict = source_data.model_dump()
    source_dict["created_at"] = datetime.utcnow()
    source_dict["updated_at"] = datetime.utcnow()
    source_dict["created_by"] = current_user.username
    source_dict["enabled"] = True
    
    await db.sources.insert_one(source_dict)
    
    # Log audit entry
    await _log_audit(
        db, "create", "source", source_data.name,
        current_user.username, {"source": source_dict}
    )
    
    source_dict.pop("_id", None)
    return NewsSource(**source_dict)


@router.put("/sources/{source_id}", response_model=NewsSource)
async def update_source(
    source_id: str,
    source_update: NewsSourceUpdate,
    current_user: User = Depends(get_current_admin_user)
):
    """Update a news source (admin only)."""
    db = get_database()
    
    # Check if source exists
    existing = await db.sources.find_one({"name": source_id})
    if not existing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Source not found"
        )
    
    # Prepare update data
    update_data = source_update.model_dump(exclude_unset=True)
    if not update_data:
        existing.pop("_id", None)
        return NewsSource(**existing)
    
    update_data["updated_at"] = datetime.utcnow()
    
    # Update source
    await db.sources.update_one(
        {"name": source_id},
        {"$set": update_data}
    )
    
    # Log audit entry
    await _log_audit(
        db, "update", "source", source_id,
        current_user.username, {"updates": update_data}
    )
    
    # Return updated source
    updated = await db.sources.find_one({"name": source_id})
    updated.pop("_id", None)
    return NewsSource(**updated)


@router.delete("/sources/{source_id}")
async def delete_source(
    source_id: str,
    current_user: User = Depends(get_current_admin_user)
):
    """Delete a news source (admin only)."""
    db = get_database()
    
    result = await db.sources.delete_one({"name": source_id})
    
    if result.deleted_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Source not found"
        )
    
    # Log audit entry
    await _log_audit(
        db, "delete", "source", source_id,
        current_user.username, {}
    )
    
    return {"message": "Source deleted successfully"}


@router.put("/sources/{source_id}/enable")
async def enable_source(
    source_id: str,
    current_user: User = Depends(get_current_admin_user)
):
    """Enable a news source (admin only)."""
    db = get_database()
    
    result = await db.sources.update_one(
        {"name": source_id},
        {"$set": {"enabled": True, "updated_at": datetime.utcnow()}}
    )
    
    if result.matched_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Source not found"
        )
    
    # Log audit entry
    await _log_audit(
        db, "enable", "source", source_id,
        current_user.username, {}
    )
    
    return {"message": "Source enabled successfully"}


@router.put("/sources/{source_id}/disable")
async def disable_source(
    source_id: str,
    current_user: User = Depends(get_current_admin_user)
):
    """Disable a news source (admin only)."""
    db = get_database()
    
    result = await db.sources.update_one(
        {"name": source_id},
        {"$set": {"enabled": False, "updated_at": datetime.utcnow()}}
    )
    
    if result.matched_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Source not found"
        )
    
    # Log audit entry
    await _log_audit(
        db, "disable", "source", source_id,
        current_user.username, {}
    )
    
    return {"message": "Source disabled successfully"}


@router.put("/sources/{source_id}/flag")
async def flag_source(
    source_id: str,
    reason: str,
    current_user: User = Depends(get_current_admin_user)
):
    """Flag a news source for review (admin only)."""
    db = get_database()
    
    result = await db.sources.update_one(
        {"name": source_id},
        {
            "$set": {
                "flagged": True,
                "flag_reason": reason,
                "flagged_by": current_user.username,
                "flagged_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
        }
    )
    
    if result.matched_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Source not found"
        )
    
    # Log audit entry
    await _log_audit(
        db, "flag", "source", source_id,
        current_user.username, {"reason": reason}
    )
    
    return {"message": "Source flagged successfully"}


# Audit Log Endpoints

@router.get("/audit-log", response_model=List[AuditLog])
async def get_audit_log(
    skip: int = 0,
    limit: int = 100,
    entity_type: Optional[str] = None,
    user: Optional[str] = None,
    current_user: User = Depends(get_current_admin_user)
):
    """Get audit log entries (admin only)."""
    db = get_database()
    
    query = {}
    if entity_type:
        query["entity_type"] = entity_type
    if user:
        query["user"] = user
    
    cursor = db.audit_log.find(query).sort("timestamp", -1).skip(skip).limit(limit)
    logs = await cursor.to_list(length=limit)
    
    # Remove MongoDB _id
    for log in logs:
        log.pop("_id", None)
    
    return [AuditLog(**log) for log in logs]


# Dashboard Stats

@router.get("/stats")
async def get_admin_stats(
    current_user: User = Depends(get_current_admin_user)
):
    """Get admin dashboard statistics (admin only)."""
    db = get_database()
    
    # Count totals
    total_users = await db.users.count_documents({})
    total_sources = await db.sources.count_documents({})
    enabled_sources = await db.sources.count_documents({"enabled": True})
    flagged_sources = await db.sources.count_documents({"flagged": True})
    total_articles = await db.articles.count_documents({})
    total_stories = await db.stories.count_documents({})
    
    # User statistics
    admin_count = await db.users.count_documents({"role": "admin"})
    disabled_users = await db.users.count_documents({"disabled": True})
    
    # Recent activity
    recent_users = await db.users.count_documents({
        "created_at": {"$gte": datetime.utcnow().replace(hour=0, minute=0, second=0)}
    })
    
    return {
        "users": {
            "total": total_users,
            "admins": admin_count,
            "disabled": disabled_users,
            "recent_signups": recent_users
        },
        "sources": {
            "total": total_sources,
            "enabled": enabled_sources,
            "disabled": total_sources - enabled_sources,
            "flagged": flagged_sources
        },
        "content": {
            "articles": total_articles,
            "stories": total_stories
        }
    }


# Helper function

async def _log_audit(db, action: str, entity_type: str, entity_id: str, 
                     user: str, details: dict, ip_address: str = None):
    """Log an audit entry."""
    log_entry = {
        "action": action,
        "entity_type": entity_type,
        "entity_id": entity_id,
        "user": user,
        "timestamp": datetime.utcnow(),
        "details": details,
        "ip_address": ip_address
    }
    
    await db.audit_log.insert_one(log_entry)
