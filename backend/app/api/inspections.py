from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.schemas.inspection import InspectionCreate, InspectionCounterSign
from app.services.inspection_service import create_inspection, list_inspections, get_inspection
from app.services.audit_service import create_audit_log
from app.middleware.rbac import require_permission
from app.models.user import User
from datetime import datetime
import uuid

router = APIRouter()

@router.get("/bridges/{bridge_id}/inspections")
async def get_bridge_inspections(
    bridge_id: uuid.UUID, 
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_permission("inspection", "read"))
):
    res = await list_inspections(db, bridge_id, page, limit)
    items = []
    for insp in res["items"]:
        items.append({
            "inspection_id": str(insp.id),
            "inspection_type": insp.inspection_type,
            "inspection_date": insp.scheduled_date.strftime("%Y-%m-%d") if insp.scheduled_date else None,
            "inspector_name": insp.inspector.full_name if insp.inspector else "Official Inspector",
            "overall_condition": insp.overall_condition or "GOOD",
            "inspection_status": insp.status,
            "next_inspection_date": insp.next_inspection_date.strftime("%Y-%m-%d") if insp.next_inspection_date else None,
            "findings": insp.findings or insp.overall_comments or "Inspection completed with standard evaluation",
            "recommendations": insp.recommendations,
            "photo_evidence_url": insp.photo_evidence_url,
            "geofence_verified": insp.geofence_verified,
            "geofence_distance_meters": insp.geofence_distance_meters,
            "inspector_gps_latitude": insp.inspector_gps_latitude,
            "inspector_gps_longitude": insp.inspector_gps_longitude,
            "counter_signed_by": str(insp.counter_signed_by) if insp.counter_signed_by else None,
            "counter_signed_by_name": insp.verifier_engineer.full_name if insp.verifier_engineer else None,
            "counter_signed_at": insp.counter_signed_at.strftime("%Y-%m-%d %H:%M") if insp.counter_signed_at else None,
            "verification_remarks": insp.verification_remarks,
            "components": [
                {
                    "component_id": str(c.id),
                    "component_type": c.component_type,
                    "condition_rating": c.condition_rating,
                    "observations": c.observations or c.notes,
                    "recommendation": c.recommendation,
                } for c in getattr(insp, 'components', [])
            ],
            "defects": [
                {
                    "defect_id": str(d.id),
                    "defect_type": d.defect_type,
                    "severity": d.severity,
                    "description": d.description,
                    "status": d.status,
                    "immediate_action_required": d.immediate_action_required,
                } for d in getattr(insp, 'defects', [])
            ]
        })
    return items

@router.post("/bridges/{bridge_id}/inspections", status_code=status.HTTP_201_CREATED)
async def post_inspection(
    bridge_id: uuid.UUID, 
    data: InspectionCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_permission("inspection", "create"))
):
    insp = await create_inspection(db, bridge_id, data, user)
    return {
        "inspection_id": str(insp.id),
        "bridge_id": str(bridge_id),
        "inspection_type": insp.inspection_type,
        "inspection_status": insp.status,
        "overall_condition": insp.overall_condition,
        "geofence_verified": insp.geofence_verified,
        "geofence_distance_meters": insp.geofence_distance_meters,
        "photo_evidence_url": insp.photo_evidence_url,
    }

@router.get("/inspections/{id}")
async def get_inspection_by_id(
    id: uuid.UUID, 
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_permission("inspection", "read"))
):
    insp = await get_inspection(db, id)
    if not insp:
        raise HTTPException(status_code=404, detail="Inspection not found")
        
    return {
        "inspection_id": str(insp.id),
        "bridge_id": str(insp.bridge_id),
        "inspection_type": insp.inspection_type,
        "inspection_date": insp.scheduled_date.strftime("%Y-%m-%d") if insp.scheduled_date else None,
        "inspector_name": insp.inspector.full_name if insp.inspector else "Official Inspector",
        "weather_condition": insp.weather_condition,
        "overall_condition": insp.overall_condition or "GOOD",
        "findings": insp.findings or insp.overall_comments,
        "recommendations": insp.recommendations,
        "inspection_status": insp.status,
        "photo_evidence_url": insp.photo_evidence_url,
        "geofence_verified": insp.geofence_verified,
        "geofence_distance_meters": insp.geofence_distance_meters,
        "inspector_gps_latitude": insp.inspector_gps_latitude,
        "inspector_gps_longitude": insp.inspector_gps_longitude,
        "counter_signed_by": str(insp.counter_signed_by) if insp.counter_signed_by else None,
        "counter_signed_by_name": insp.verifier_engineer.full_name if insp.verifier_engineer else None,
        "counter_signed_at": insp.counter_signed_at.strftime("%Y-%m-%d %H:%M") if insp.counter_signed_at else None,
        "verification_remarks": insp.verification_remarks,
        "components": [
            {
                "component_id": str(c.id),
                "component_type": c.component_type,
                "condition_rating": c.condition_rating,
                "observations": c.observations or c.notes,
                "recommendation": c.recommendation,
            } for c in getattr(insp, 'components', [])
        ],
        "defects": [
            {
                "defect_id": str(d.id),
                "defect_type": d.defect_type,
                "severity": d.severity,
                "component_type": getattr(d, 'component_type', None),
                "location_on_bridge": d.location_on_bridge,
                "description": d.description,
                "immediate_action_required": d.immediate_action_required,
                "status": d.status,
            } for d in getattr(insp, 'defects', [])
        ]
    }

@router.post("/inspections/{id}/counter-sign")
async def counter_sign_inspection(
    id: uuid.UUID,
    data: InspectionCounterSign,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_permission("inspection", "update"))
):
    role_name = user.role.name if user.role else ""
    if role_name not in ["EXECUTIVE_ENGINEER", "DEPARTMENT_HEAD", "ADMIN"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Only Executive Engineers or Department Heads can counter-sign inspection reports"
        )
        
    insp = await get_inspection(db, id)
    if not insp:
        raise HTTPException(status_code=404, detail="Inspection not found")
        
    insp.counter_signed_by = user.id
    insp.counter_signed_at = datetime.utcnow()
    insp.verification_remarks = data.verification_remarks or f"Field report & condition assessment reviewed and counter-signed by {user.full_name} ({role_name})"
    
    await create_audit_log(db, "inspection", insp.id, "COUNTER_SIGN", user.id, None, {
        "counter_signed_by": str(user.id),
        "counter_signed_by_name": user.full_name,
        "remarks": insp.verification_remarks
    })
    
    await db.commit()
    await db.refresh(insp)
    return {
        "inspection_id": str(insp.id),
        "counter_signed_by": str(user.id),
        "counter_signed_by_name": user.full_name,
        "counter_signed_at": insp.counter_signed_at.strftime("%Y-%m-%d %H:%M"),
        "verification_remarks": insp.verification_remarks
    }
