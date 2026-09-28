from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, or_, func
from app.models.bridge import Bridge, BridgeLocation, BridgeEngineering
from app.models.condition import ConditionAssessment
from app.models.inspection import Inspection
from app.models.maintenance import MaintenanceRecord
from app.schemas.bridge import BridgeCreate, BridgeUpdate
from app.services.audit_service import create_audit_log
from app.services.lifecycle_service import process_lifecycle_event
from datetime import datetime, timedelta
import uuid

async def create_bridge(db: AsyncSession, data: BridgeCreate, user):
    bridge_code = getattr(data, 'bridge_code', None) or getattr(data, 'bridge_id_str', None) or f"BR-GJ-{uuid.uuid4().hex[:4].upper()}"
    bridge_name = getattr(data, 'bridge_name', None) or getattr(data, 'name', None) or "Bridge"
    asset_type = getattr(data, 'asset_type', None) or "BRIDGE"
    
    bridge = Bridge(
        bridge_id_str=bridge_code,
        name=bridge_name,
        asset_type=asset_type,
        bridge_type=data.bridge_type,
        structure_category=data.structure_category,
        current_status=data.current_status or "PLANNED",
        department=data.department,
        owning_authority=data.owning_authority,
        maintaining_authority=data.maintaining_authority,
        traffic_status=data.traffic_status,
    )
    db.add(bridge)
    await db.flush()

    location = BridgeLocation(
        bridge_id=bridge.id,
        latitude=data.location.latitude,
        longitude=data.location.longitude,
        district=data.location.district,
        state=data.location.state or "Gujarat",
        river_crossing=getattr(data.location, 'river_crossing', None),
        road_name=getattr(data.location, 'road_name', None),
        taluka=getattr(data.location, 'taluka', None),
    )
    db.add(location)

    engineering = BridgeEngineering(
        bridge_id=bridge.id,
        total_length=data.engineering.total_length,
        number_of_spans=data.engineering.number_of_spans,
        deck_width=data.engineering.deck_width,
        design_life=data.engineering.design_life or 100,
        year_built=getattr(data.engineering, 'year_built', None) or getattr(data.engineering, 'year_constructed', None),
    )
    db.add(engineering)
    await db.commit()
    await db.refresh(bridge)

    await create_audit_log(
        db_session=db,
        entity_type="bridge",
        entity_id=bridge.id,
        action="CREATE",
        user_id=user.id,
        old_val=None,
        new_val={"bridge_name": bridge.name, "bridge_code": bridge.bridge_id_str}
    )

    await process_lifecycle_event(
        db, 
        bridge_id=bridge.id,
        event_type="PROPOSED",
        event_date=datetime.utcnow(),
        description="Initial creation of bridge record",
        user_id=user.id
    )

    return await get_bridge(db, bridge.id)

async def list_bridges(db: AsyncSession, filters: dict, page: int = 1, limit: int = 20):
    offset = (page - 1) * limit
    stmt = select(Bridge).join(BridgeLocation, Bridge.id == BridgeLocation.bridge_id, isouter=True)
    
    if filters.get("status"):
        stmt = stmt.where(Bridge.current_status == filters["status"])
    if filters.get("asset_type") and filters["asset_type"] != "ALL":
        stmt = stmt.where(Bridge.asset_type == filters["asset_type"])
    if filters.get("district"):
        stmt = stmt.where(BridgeLocation.district == filters["district"])
    if filters.get("bridge_type"):
        stmt = stmt.where(Bridge.bridge_type == filters["bridge_type"])
    if filters.get("search"):
        s = f"%{filters['search']}%"
        stmt = stmt.where(or_(Bridge.name.ilike(s), Bridge.bridge_id_str.ilike(s)))
    
    # Count total
    count_stmt = select(func.count(Bridge.id))
    if filters.get("status"): count_stmt = count_stmt.where(Bridge.current_status == filters["status"])
    if filters.get("asset_type") and filters["asset_type"] != "ALL": count_stmt = count_stmt.where(Bridge.asset_type == filters["asset_type"])
    total_res = await db.execute(count_stmt)
    total = total_res.scalar() or 0

    stmt_page = stmt.order_by(Bridge.created_at.desc()).offset(offset).limit(limit)
    result = await db.execute(stmt_page)
    bridges = result.scalars().all()
    
    # Batch fetch latest conditions for these bridges
    bridge_ids = [b.id for b in bridges]
    conditions_map = {}
    if bridge_ids:
        cond_stmt = select(ConditionAssessment).where(
            ConditionAssessment.bridge_id.in_(bridge_ids)
        ).order_by(ConditionAssessment.assessment_date.desc())
        cond_res = await db.execute(cond_stmt)
        for c in cond_res.scalars().all():
            if c.bridge_id not in conditions_map:
                conditions_map[c.bridge_id] = c

    items = []
    for b in bridges:
        cond = conditions_map.get(b.id)
        items.append({
            "id": str(b.id),
            "bridge_id": str(b.id),
            "bridge_code": b.bridge_id_str,
            "bridge_id_str": b.bridge_id_str,
            "name": b.name,
            "bridge_name": b.name,
            "asset_type": b.asset_type or "BRIDGE",
            "bridge_type": b.bridge_type,
            "structure_category": b.structure_category,
            "current_status": b.current_status,
            "year_constructed": b.year_constructed,
            "district": b.district,
            "state": b.state,
            "latitude": b.latitude,
            "longitude": b.longitude,
            "latest_health_index": round(cond.health_index_score, 1) if cond else None,
            "latest_condition_category": cond.condition_category if cond else None,
            "road_name": b.road_name,
        })
        
    return {"items": items, "total": total, "page": page, "limit": limit}

async def get_bridge(db: AsyncSession, bridge_id: uuid.UUID):
    stmt = select(Bridge).where(Bridge.id == bridge_id)
    result = await db.execute(stmt)
    b = result.scalars().first()
    if not b:
        return None

    # Get latest condition
    cond_stmt = select(ConditionAssessment).where(
        ConditionAssessment.bridge_id == b.id
    ).order_by(ConditionAssessment.assessment_date.desc()).limit(1)
    cond_res = await db.execute(cond_stmt)
    cond = cond_res.scalars().first()

    # Get latest inspection
    insp_stmt = select(Inspection).where(
        Inspection.bridge_id == b.id
    ).order_by(Inspection.scheduled_date.desc()).limit(1)
    insp_res = await db.execute(insp_stmt)
    insp = insp_res.scalars().first()

    # Get active maintenance
    maint_stmt = select(MaintenanceRecord).where(
        MaintenanceRecord.bridge_id == b.id,
        MaintenanceRecord.status.in_(["REPORTED", "APPROVED", "IN_PROGRESS"])
    ).order_by(MaintenanceRecord.reported_date.desc())
    maint_res = await db.execute(maint_stmt)
    active_maint = maint_res.scalars().all()

    return {
        "id": str(b.id),
        "bridge_id": str(b.id),
        "bridge_code": b.bridge_id_str,
        "bridge_name": b.name,
        "name": b.name,
        "asset_type": b.asset_type or "BRIDGE",
        "bridge_type": b.bridge_type,
        "structure_category": b.structure_category,
        "current_status": b.current_status,
        "department": b.department,
        "owning_authority": b.owning_authority,
        "maintaining_authority": b.maintaining_authority,
        "road_name": b.road_name,
        "route_number": getattr(b, 'route_number', None) or b.road_name,
        "year_constructed": b.year_constructed,
        "date_commissioned": b.created_at.strftime("%Y-%m-%d") if b.created_at else None,
        "traffic_status": b.traffic_status or "Normal",
        "daily_traffic_estimate": b.daily_traffic_estimate,
        "load_restriction": str(b.load_restriction) if b.load_restriction else None,
        "speed_restriction": b.speed_restriction,
        "description": f"{b.structure_category} {b.asset_type.lower() if hasattr(b, 'asset_type') and b.asset_type else 'structure'} in {b.district}",
        "created_at": b.created_at.isoformat() if b.created_at else datetime.utcnow().isoformat(),
        "updated_at": b.updated_at.isoformat() if b.updated_at else datetime.utcnow().isoformat(),
        "location": {
            "state": b.state,
            "district": b.district,
            "taluka": b.location.taluka if b.location else None,
            "village_or_city": b.district,
            "latitude": b.latitude,
            "longitude": b.longitude,
            "elevation": 50.0,
            "chainage_start": b.location.chainage_start if b.location else None,
            "chainage_end": b.location.chainage_end if b.location else None,
        },
        "engineering": {
            "total_length": b.engineering.total_length if b.engineering else None,
            "carriageway_width": (b.engineering.carriageway_width if b.engineering and b.engineering.carriageway_width else b.engineering.deck_width) if b.engineering else None,
            "deck_width": b.engineering.deck_width if b.engineering else None,
            "overall_width": b.engineering.overall_width if b.engineering else 12.0,
            "number_of_lanes": b.engineering.number_of_lanes if b.engineering else 2,
            "number_of_spans": b.engineering.number_of_spans if b.engineering else 4,
            "superstructure_type": b.engineering.superstructure_type if b.engineering else "Concrete Girder",
            "substructure_type": b.engineering.substructure_type if b.engineering else "RCC Pier",
            "foundation_type": b.engineering.foundation_type if b.engineering else "Well Foundation",
            "construction_material": "Reinforced Cement Concrete",
            "deck_material": b.engineering.deck_material if b.engineering else "RCC Slab",
            "design_loading": "IRC Class 70R",
            "design_speed": 80,
            "design_life": b.engineering.design_life if b.engineering else 100,
            "tunnel_type": b.engineering.tunnel_type if b.engineering else None,
            "bore_diameter": b.engineering.bore_diameter if b.engineering else None,
            "ventilation_system": b.engineering.ventilation_system if b.engineering else None,
            "pavement_type": b.engineering.pavement_type if b.engineering else None,
            "culvert_type": b.engineering.culvert_type if b.engineering else None,
            "opening_span": b.engineering.opening_span if b.engineering else None,
            "clear_height": b.engineering.clear_height if b.engineering else None,
        },
        "latest_condition": {
            "overall_health_index": round(cond.health_index_score, 1),
            "condition_category": cond.condition_category,
            "structural_score": cond.structural_score or 75.0,
            "functional_score": cond.functional_score or 80.0,
            "safety_score": cond.safety_score or 70.0,
            "assessment_date": cond.assessment_date.strftime("%Y-%m-%d") if cond.assessment_date else "2026-08-12",
            "calculation_version": cond.calculation_version,
        } if cond else None,
        "latest_inspection": {
            "inspection_id": str(insp.id),
            "inspection_type": insp.inspection_type,
            "inspection_date": insp.scheduled_date.strftime("%Y-%m-%d") if insp.scheduled_date and hasattr(insp.scheduled_date, 'strftime') else datetime.utcnow().strftime("%Y-%m-%d"),
            "overall_condition": insp.overall_condition or (cond.condition_category if cond else "GOOD"),
            "next_inspection_date": (
                insp.next_inspection_date.strftime("%Y-%m-%d") if getattr(insp, 'next_inspection_date', None) and hasattr(insp.next_inspection_date, 'strftime')
                else (insp.scheduled_date + timedelta(days=365)).strftime("%Y-%m-%d") if insp.scheduled_date and hasattr(insp.scheduled_date, 'strftime')
                else "2027-08-12"
            ),
        } if insp else None,
        "active_maintenance": [
            {
                "maintenance_id": str(m.id),
                "maintenance_type": m.maintenance_type,
                "issue_description": m.description or "Routine upkeep",
                "status": m.status,
                "priority": m.priority,
                "reported_date": m.reported_date.strftime("%Y-%m-%d") if m.reported_date else None,
                "start_date": m.start_date.strftime("%Y-%m-%d") if m.start_date else None,
                "completion_date": m.completion_date.strftime("%Y-%m-%d") if m.completion_date else None,
                "estimated_cost": m.estimated_cost,
                "actual_cost": m.actual_cost,
            } for m in active_maint
        ]
    }

async def update_bridge(db: AsyncSession, bridge_id: uuid.UUID, data: BridgeUpdate, user):
    stmt = select(Bridge).where(Bridge.id == bridge_id)
    res = await db.execute(stmt)
    bridge = res.scalars().first()
    if not bridge:
        return None
        
    old_val = {
        "name": bridge.name,
        "bridge_type": bridge.bridge_type,
        "structure_category": bridge.structure_category,
        "department": bridge.department
    }
    
    if data.name: bridge.name = data.name
    if data.bridge_type: bridge.bridge_type = data.bridge_type
    if data.structure_category: bridge.structure_category = data.structure_category
    if data.department: bridge.department = data.department
    
    new_val = {
        "name": bridge.name,
        "bridge_type": bridge.bridge_type,
        "structure_category": bridge.structure_category,
        "department": bridge.department
    }
    
    await create_audit_log(db, "bridge", bridge.id, "UPDATE", user.id, old_val, new_val)
    await db.commit()
    await db.refresh(bridge)
    return await get_bridge(db, bridge.id)

async def delete_bridge(db: AsyncSession, bridge_id: uuid.UUID, user):
    stmt = select(Bridge).where(Bridge.id == bridge_id)
    res = await db.execute(stmt)
    bridge = res.scalars().first()
    if not bridge:
        return False
        
    await create_audit_log(
        db, 
        "bridge", 
        bridge.id, 
        "DELETE", 
        user.id, 
        {"id": str(bridge.id), "bridge_code": bridge.bridge_id_str, "name": bridge.name, "district": bridge.district}, 
        None
    )
    await db.delete(bridge)
    await db.commit()
    return True
