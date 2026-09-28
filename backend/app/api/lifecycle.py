from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.schemas.lifecycle import LifecycleEventCreate
from app.services.lifecycle_service import process_lifecycle_event, list_lifecycle_events
from app.middleware.rbac import require_permission
from app.models.user import User
import uuid

router = APIRouter()

@router.get("/bridges/{id}/lifecycle")
async def get_lifecycle_events(
    id: uuid.UUID, 
    page: int = Query(1, ge=1), 
    limit: int = Query(50, ge=1, le=100), 
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_permission("lifecycle", "read"))
):
    res = await list_lifecycle_events(db, id, page, limit)
    items = []
    for evt in res["items"]:
        items.append({
            "event_id": str(evt.id),
            "event_type": evt.event_type,
            "event_date": evt.event_date.strftime("%Y-%m-%d") if evt.event_date else None,
            "performed_by_name": evt.performed_by_name or "System Officer",
            "department": getattr(evt.performer, "department", "PWD Gujarat") if evt.performer else "PWD Gujarat",
            "description": evt.description or f"{evt.event_type} registered",
            "previous_status": evt.previous_status,
            "new_status": evt.new_status,
            "remarks": evt.remarks,
            "created_at": evt.event_date.isoformat() if evt.event_date else None,
        })
    return items

@router.post("/bridges/{id}/lifecycle")
async def create_lifecycle_event(
    id: uuid.UUID, 
    event: LifecycleEventCreate, 
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_permission("lifecycle", "create"))
):
    try:
        evt = await process_lifecycle_event(
            db, 
            bridge_id=id, 
            event_type=event.event_type, 
            event_date=event.event_date, 
            description=event.description,
            user_id=user.id
        )
        return {
            "event_id": str(evt.id),
            "event_type": evt.event_type,
            "event_date": evt.event_date.strftime("%Y-%m-%d") if evt.event_date else None,
            "previous_status": evt.previous_status,
            "new_status": evt.new_status,
            "description": evt.description,
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
