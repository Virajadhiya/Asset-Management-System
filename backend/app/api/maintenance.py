from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from app.database import get_db
from app.schemas.maintenance import MaintenanceCreate, MaintenanceStatusUpdate
from app.services.maintenance_service import create_maintenance, update_maintenance_status
from app.middleware.rbac import require_permission
from app.models.user import User
from app.models.maintenance import MaintenanceRecord
import uuid

router = APIRouter()

@router.get("/bridges/{id}/maintenance")
async def get_bridge_maintenance(
    id: uuid.UUID, 
    page: int = Query(1, ge=1), 
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_permission("maintenance", "read"))
):
    offset = (page - 1) * limit
    stmt = (
        select(MaintenanceRecord)
        .where(MaintenanceRecord.bridge_id == id)
        .order_by(desc(MaintenanceRecord.reported_date))
        .offset(offset)
        .limit(limit)
    )
    res = await db.execute(stmt)
    items = res.scalars().all()
    
    return [
        {
            "maintenance_id": str(m.id),
            "bridge_id": str(m.bridge_id),
            "maintenance_type": m.maintenance_type,
            "issue_description": m.description or "Routine Maintenance",
            "priority": m.priority,
            "status": m.status,
            "reported_date": m.reported_date.strftime("%Y-%m-%d") if m.reported_date else None,
            "start_date": m.start_date.strftime("%Y-%m-%d") if m.start_date else None,
            "completion_date": m.completion_date.strftime("%Y-%m-%d") if m.completion_date else None,
            "estimated_cost": m.estimated_cost,
            "actual_cost": m.actual_cost,
            "sanction_number": m.sanction_number,
            "sanctioned_amount": m.sanctioned_amount,
            "tender_number": m.tender_number,
            "work_order_number": m.work_order_number,
            "tender_value": m.tender_value,
            "assigned_contractor": m.assigned_contractor or m.contractor_name,
            "contractor_name": m.assigned_contractor or m.contractor_name,
            "estimated_by_name": m.estimator.full_name if m.estimator else None,
            "approved_by_name": m.approver.full_name if m.approver else None,
            "verified_by_name": m.verifier.full_name if m.verifier else None,
        } for m in items
    ]

@router.post("/bridges/{id}/maintenance", status_code=status.HTTP_201_CREATED)
async def post_maintenance(
    id: uuid.UUID, 
    data: MaintenanceCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_permission("maintenance", "create"))
):
    m = await create_maintenance(db, id, data, user)
    return {
        "maintenance_id": str(m.id),
        "bridge_id": str(m.bridge_id),
        "status": m.status,
        "maintenance_type": m.maintenance_type,
        "priority": m.priority,
    }

@router.put("/maintenance/{id}/status")
async def put_maintenance_status(
    id: uuid.UUID, 
    data: MaintenanceStatusUpdate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_permission("maintenance", "update"))
):
    record = await update_maintenance_status(db, id, data, user)
    if not record:
        raise HTTPException(status_code=404, detail="Maintenance record not found")
        
    return {
        "maintenance_id": str(record.id),
        "status": record.status,
        "action": data.action,
        "updated": True,
        "estimated_cost": record.estimated_cost,
        "sanction_number": record.sanction_number,
        "sanctioned_amount": record.sanctioned_amount,
        "tender_number": record.tender_number,
        "work_order_number": record.work_order_number,
        "tender_value": record.tender_value,
        "assigned_contractor": record.assigned_contractor,
        "actual_cost": record.actual_cost,
    }
