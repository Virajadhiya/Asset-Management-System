from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from app.database import get_db
from app.models.bridge import Bridge, BridgeLocation
from app.models.condition import ConditionAssessment
from app.middleware.rbac import require_permission
from app.models.user import User

router = APIRouter()

@router.get("/bridges")
async def get_gis_bridges(
    condition: str = None, 
    status: str = None, 
    district: str = None,
    asset_type: str = None,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_permission("bridge", "read"))
):
    stmt = select(Bridge).join(BridgeLocation, Bridge.id == BridgeLocation.bridge_id, isouter=True)
    if status:
        stmt = stmt.where(Bridge.current_status == status)
    if district:
        stmt = stmt.where(BridgeLocation.district == district)
    if asset_type and asset_type != "ALL":
        stmt = stmt.where(Bridge.asset_type == asset_type)
        
    res = await db.execute(stmt)
    bridges = res.scalars().all()

    # Fetch conditions
    cond_stmt = select(ConditionAssessment).order_by(desc(ConditionAssessment.assessment_date))
    cond_res = await db.execute(cond_stmt)
    conditions = cond_res.scalars().all()
    cond_map = {}
    for c in conditions:
        if c.bridge_id not in cond_map:
            cond_map[c.bridge_id] = c
    
    items = []
    for b in bridges:
        cond = cond_map.get(b.id)
        cond_cat = cond.condition_category if cond else None
        if condition and cond_cat != condition:
            continue
            
        items.append({
            "id": str(b.id),
            "bridge_id": str(b.id),
            "bridge_code": b.bridge_id_str,
            "bridge_name": b.name,
            "name": b.name,
            "asset_type": b.asset_type or "BRIDGE",
            "latitude": b.latitude,
            "longitude": b.longitude,
            "status": b.current_status,
            "current_status": b.current_status,
            "condition": cond_cat or "GOOD",
            "condition_category": cond_cat or "GOOD",
            "health_index": round(cond.health_index_score, 1) if cond else None,
            "bridge_type": b.bridge_type,
            "district": b.district,
            "year_constructed": b.year_constructed,
        })
        
    # Return list directly and wrapper fields so all frontend expectations work
    return items
