from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from app.models.lifecycle import LifecycleEvent
from app.models.bridge import Bridge
from app.services.audit_service import create_audit_log

VALID_TRANSITIONS = {
    'PLANNED': ['UNDER_CONSTRUCTION'],
    'UNDER_CONSTRUCTION': ['OPERATIONAL'],
    'OPERATIONAL': ['UNDER_MAINTENANCE', 'UNDER_REHABILITATION', 'CLOSED', 'DECOMMISSIONED'],
    'UNDER_MAINTENANCE': ['OPERATIONAL', 'CLOSED'],
    'UNDER_REHABILITATION': ['OPERATIONAL', 'CLOSED'],
    'CLOSED': ['OPERATIONAL', 'DECOMMISSIONED'],
    'DECOMMISSIONED': [],
}

EVENT_TO_NEW_STATUS = {
    'CONSTRUCTION_STARTED': 'UNDER_CONSTRUCTION',
    'COMMISSIONED': 'OPERATIONAL',
    'MAINTENANCE_STARTED': 'UNDER_MAINTENANCE',
    'MAINTENANCE_COMPLETED': 'OPERATIONAL',
    'REHABILITATION_STARTED': 'UNDER_REHABILITATION',
    'REHABILITATION_COMPLETED': 'OPERATIONAL',
    'CLOSED': 'CLOSED',
    'REOPENED': 'OPERATIONAL',
    'DECOMMISSIONED': 'DECOMMISSIONED',
}

async def process_lifecycle_event(db: AsyncSession, bridge_id, event_type: str, event_date: datetime, description: str, user_id):
    # Fetch bridge
    stmt = select(Bridge).where(Bridge.id == bridge_id)
    result = await db.execute(stmt)
    bridge = result.scalars().first()
    
    if not bridge:
        raise ValueError("Bridge not found")
        
    current_status = bridge.current_status
    new_status = EVENT_TO_NEW_STATUS.get(event_type)
    
    event = LifecycleEvent(
        bridge_id=bridge_id,
        event_type=event_type,
        event_date=event_date,
        description=description,
        previous_status=current_status,
        new_status=new_status if new_status else current_status,
        recorded_by=user_id
    )
    db.add(event)
    
    if new_status and new_status != current_status:
        if new_status not in VALID_TRANSITIONS.get(current_status, []):
            raise ValueError(f"Invalid transition from {current_status} to {new_status}")
        
        # Update bridge status
        old_val = {"current_status": current_status}
        new_val = {"current_status": new_status}
        bridge.current_status = new_status
        
        await create_audit_log(
            db_session=db,
            entity_type="bridge",
            entity_id=bridge_id,
            action="UPDATE_STATUS",
            user_id=user_id,
            old_val=old_val,
            new_val=new_val
        )

    await db.commit()
    await db.refresh(event)
    return event

async def list_lifecycle_events(db: AsyncSession, bridge_id, page: int = 1, limit: int = 20):
    offset = (page - 1) * limit
    stmt = select(LifecycleEvent).where(LifecycleEvent.bridge_id == bridge_id).order_by(desc(LifecycleEvent.event_date)).offset(offset).limit(limit)
    result = await db.execute(stmt)
    items = result.scalars().all()
    
    count_stmt = select(LifecycleEvent).where(LifecycleEvent.bridge_id == bridge_id)
    count_result = await db.execute(count_stmt)
    total = len(count_result.scalars().all())
    
    return {"items": items, "total": total, "page": page, "limit": limit}
