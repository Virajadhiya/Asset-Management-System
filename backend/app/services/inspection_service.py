from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.inspection import Inspection, InspectionComponent, Defect
from app.models.condition import ConditionAssessment
from app.models.bridge import BridgeEngineering, BridgeLocation
from app.schemas.inspection import InspectionCreate
from app.services.audit_service import create_audit_log
from app.services.lifecycle_service import process_lifecycle_event
from app.services.health_index import calculate_health_index
from datetime import datetime
import uuid
import math

def haversine_distance_meters(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    R = 6371000.0  # Earth radius in meters
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)
    a = math.sin(delta_phi / 2.0) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2.0) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
    return round(R * c, 1)

async def create_inspection(db: AsyncSession, bridge_id: uuid.UUID, data: InspectionCreate, user):
    # Geofence validation against asset physical location
    geofence_distance = None
    geofence_verified = True
    
    if data.inspector_gps_latitude is not None and data.inspector_gps_longitude is not None:
        loc_stmt = select(BridgeLocation).where(BridgeLocation.bridge_id == bridge_id)
        loc_res = await db.execute(loc_stmt)
        location = loc_res.scalars().first()
        if location and location.latitude is not None and location.longitude is not None:
            geofence_distance = haversine_distance_meters(
                data.inspector_gps_latitude, data.inspector_gps_longitude,
                location.latitude, location.longitude
            )
            # MoRTH / PWD standard: on-site physical presence verified within 150m
            geofence_verified = (geofence_distance <= 150.0)
        else:
            geofence_verified = True
    else:
        # If inspector didn't supply GPS, flag as unverified
        geofence_verified = False

    inspection = Inspection(
        bridge_id=bridge_id,
        inspector_id=user.id,
        inspection_type=data.inspection_type,
        status="COMPLETED",
        scheduled_date=data.scheduled_date or datetime.utcnow(),
        completion_date=datetime.utcnow(),
        weather_condition=data.weather_condition or "CLEAR",
        overall_comments=data.overall_comments,
        inspector_gps_latitude=data.inspector_gps_latitude,
        inspector_gps_longitude=data.inspector_gps_longitude,
        geofence_distance_meters=geofence_distance,
        geofence_verified=geofence_verified,
        photo_evidence_url=data.photo_evidence_url,
    )
    db.add(inspection)
    await db.flush()
    
    components = []
    for c in data.components:
        comp = InspectionComponent(
            inspection_id=inspection.id,
            component_type=c.component_type,
            condition_rating=c.condition_rating,
            notes=c.notes,
            observations=c.notes
        )
        db.add(comp)
        components.append(comp)
        
    await db.flush()
    
    for d in data.defects:
        defect = Defect(
            inspection_id=inspection.id,
            component_id=d.component_id,
            severity=d.severity,
            description=d.description,
            defect_type="STRUCTURAL" if d.severity in ["HIGH", "CRITICAL"] else "GENERAL",
            immediate_action_required=(d.severity == "CRITICAL")
        )
        db.add(defect)
        
    # Get engineering details for health index
    eng_stmt = select(BridgeEngineering).where(BridgeEngineering.bridge_id == bridge_id)
    eng_res = await db.execute(eng_stmt)
    engineering = eng_res.scalars().first()
    
    year_built = engineering.year_built if engineering else None
    design_life = engineering.design_life if engineering else 100
    
    hi = calculate_health_index(components, design_life, year_built)
    
    inspection.overall_condition = hi["category"]
    inspection.findings = data.overall_comments or f"Overall condition assessed as {hi['category']} with BHI {hi['score']}."
    
    condition = ConditionAssessment(
        bridge_id=bridge_id,
        inspection_id=inspection.id,
        health_index_score=hi["score"],
        condition_category=hi["category"],
        calculation_version=hi["version"]
    )
    db.add(condition)
    
    await create_audit_log(db, "inspection", inspection.id, "CREATE", user.id, None, {
        "type": data.inspection_type,
        "geofence_verified": geofence_verified,
        "geofence_distance_meters": geofence_distance
    })
    
    await process_lifecycle_event(
        db, bridge_id, "INSPECTION_COMPLETED", datetime.utcnow(),
        f"Completed {data.inspection_type} inspection. Condition: {hi['category']}, Score: {hi['score']}.", user.id
    )
    
    await db.commit()
    await db.refresh(inspection)
    return inspection

async def list_inspections(db: AsyncSession, bridge_id: uuid.UUID, page: int = 1, limit: int = 20):
    offset = (page - 1) * limit
    stmt = select(Inspection).where(Inspection.bridge_id == bridge_id).order_by(Inspection.scheduled_date.desc()).offset(offset).limit(limit)
    res = await db.execute(stmt)
    items = res.scalars().unique().all()
    total_res = await db.execute(select(Inspection.id).where(Inspection.bridge_id == bridge_id))
    total = len(total_res.scalars().all())
    return {"items": items, "total": total, "page": page, "limit": limit}

async def get_inspection(db: AsyncSession, inspection_id: uuid.UUID):
    stmt = select(Inspection).where(Inspection.id == inspection_id)
    res = await db.execute(stmt)
    return res.scalars().unique().first()
