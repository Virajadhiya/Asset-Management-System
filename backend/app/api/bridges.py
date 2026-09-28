from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from app.database import get_db
from app.schemas.bridge import BridgeCreate, BridgeUpdate
from app.services.bridge_service import create_bridge, list_bridges, get_bridge, update_bridge, delete_bridge
from app.middleware.rbac import require_permission
from app.middleware.auth import get_current_user
from app.models.user import User
from app.models.issue import DistressIssue
import uuid

router = APIRouter()

@router.get("")
async def get_bridges(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    status: str = None,
    district: str = None,
    bridge_type: str = None,
    asset_type: str = None,
    search: str = None,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_permission("bridge", "read"))
):
    filters = {"status": status, "district": district, "bridge_type": bridge_type, "asset_type": asset_type, "search": search}
    return await list_bridges(db, filters, page, limit)

@router.post("", status_code=status.HTTP_201_CREATED)
async def post_bridge(
    data: BridgeCreate, 
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_permission("bridge", "create"))
):
    return await create_bridge(db, data, user)

@router.get("/{id}")
async def get_bridge_by_id(
    id: uuid.UUID, 
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_permission("bridge", "read"))
):
    bridge = await get_bridge(db, id)
    if not bridge:
        raise HTTPException(status_code=404, detail="Bridge not found")
    return bridge

@router.put("/{id}")
async def put_bridge(
    id: uuid.UUID, 
    data: BridgeUpdate, 
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_permission("bridge", "update"))
):
    bridge = await update_bridge(db, id, data, user)
    if not bridge:
        raise HTTPException(status_code=404, detail="Bridge not found")
    return bridge

@router.delete("/{id}")
async def delete_bridge_by_id(
    id: uuid.UUID, 
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_permission("bridge", "delete"))
):
    res = await delete_bridge(db, id, user)
    if not res:
        raise HTTPException(status_code=404, detail="Bridge not found")
    return {"message": "Deleted successfully"}

@router.get("/{id}/issues")
async def get_bridge_issues(
    id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_permission("bridge", "read"))
):
    stmt = select(DistressIssue).where(DistressIssue.bridge_id == id).order_by(desc(DistressIssue.created_at))
    res = await db.execute(stmt)
    items = res.scalars().all()
    return [
        {
            "id": str(i.id),
            "bridge_id": str(i.bridge_id),
            "bridge_code": i.bridge.bridge_id_str if i.bridge else None,
            "bridge_name": i.bridge.name if i.bridge else None,
            "title": i.title,
            "issue_type": i.title,
            "description": i.description,
            "location_details": i.location_details or i.description,
            "source": i.source,
            "severity": i.severity,
            "status": i.status,
            "photo_url": i.photo_url,
            "reported_by_name": i.reported_by_name or "Citizen Report",
            "reported_by": str(i.reported_by_id) if i.reported_by_id else None,
            "reporter_name": i.reported_by_name or "Citizen Report",
            "reporter_role": "Officer",
            "district": i.bridge.district if i.bridge else None,
            "assigned_inspector_id": str(i.assigned_inspector_id) if i.assigned_inspector_id else None,
            "assigned_inspector_name": i.assigned_inspector.full_name if i.assigned_inspector else None,
            "assigned_engineer_id": str(i.assigned_engineer_id) if i.assigned_engineer_id else None,
            "assigned_engineer_name": i.assigned_engineer.full_name if i.assigned_engineer else None,
            "target_date": i.target_date.strftime("%Y-%m-%d") if i.target_date else None,
            "target_completion_date": i.target_date.strftime("%Y-%m-%d") if i.target_date else None,
            "created_at": i.created_at.strftime("%Y-%m-%d %H:%M") if i.created_at else None,
            "updated_at": i.created_at.strftime("%Y-%m-%d %H:%M") if i.created_at else None,
        } for i in items
    ]
