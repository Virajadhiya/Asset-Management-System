from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.maintenance import MaintenanceRecord
from app.schemas.maintenance import MaintenanceCreate, MaintenanceStatusUpdate
from app.services.audit_service import create_audit_log
from app.services.lifecycle_service import process_lifecycle_event
from datetime import datetime
import uuid

async def create_maintenance(db: AsyncSession, bridge_id: uuid.UUID, data: MaintenanceCreate, user):
    record = MaintenanceRecord(
        bridge_id=bridge_id,
        maintenance_type=data.maintenance_type,
        priority=data.priority,
        status="REPORTED",
        description=data.description,
        estimated_cost=data.estimated_cost
    )
    db.add(record)
    await db.commit()
    await db.refresh(record)
    
    await create_audit_log(db, "maintenance", record.id, "CREATE", user.id, None, {"status": "REPORTED"})
    return record

async def update_maintenance_status(db: AsyncSession, maintenance_id: uuid.UUID, data: MaintenanceStatusUpdate, user):
    stmt = select(MaintenanceRecord).where(MaintenanceRecord.id == maintenance_id)
    res = await db.execute(stmt)
    record = res.scalars().first()
    if not record: return None
    
    old_status = record.status
    now = datetime.utcnow()
    action = data.action.lower()
    
    if action == "estimate":
        # Executive Engineer submits detailed DPR estimate
        record.status = "ESTIMATED"
        if data.estimated_cost is not None:
            record.estimated_cost = data.estimated_cost
        record.estimated_by = user.id
        
    elif action in ["sanction", "approve"]:
        # Department Head grants Administrative Approval & Financial Sanction
        record.status = "SANCTIONED"
        if data.sanction_number:
            record.sanction_number = data.sanction_number
        if data.sanctioned_amount is not None:
            record.sanctioned_amount = data.sanctioned_amount
        record.approved_by = user.id

    elif action == "award_tender":
        # Department Head / Executive Engineer awards tender and issues Work Order
        record.status = "TENDER_AWARDED"
        if data.tender_number:
            record.tender_number = data.tender_number
        if data.work_order_number:
            record.work_order_number = data.work_order_number
        if data.tender_value is not None:
            record.tender_value = data.tender_value
        if data.assigned_contractor:
            record.assigned_contractor = data.assigned_contractor
            record.contractor_name = data.assigned_contractor

    elif action in ["start", "start_work"]:
        # Contractor / Maintenance Officer mobilizes on site
        record.status = "IN_PROGRESS"
        record.start_date = now
        await process_lifecycle_event(
            db, 
            record.bridge_id, 
            "MAINTENANCE_STARTED", 
            now, 
            data.remarks or f"Work Order {record.work_order_number or ''} physical execution mobilized by {record.assigned_contractor or 'contractor'}", 
            user.id
        )

    elif action in ["complete", "complete_work"]:
        # Contractor finishes physical work and records actual billing
        record.status = "COMPLETED"
        record.completion_date = now
        if data.actual_cost is not None:
            record.actual_cost = data.actual_cost

    elif action in ["verify", "verify_signoff"]:
        # Executive Engineer inspects on-site quality and verifies completion
        record.status = "VERIFIED"
        record.verified_by = user.id
        await process_lifecycle_event(
            db, 
            record.bridge_id, 
            "MAINTENANCE_COMPLETED", 
            now, 
            data.remarks or f"Engineering verification passed by {user.full_name}. Asset reopened for normal traffic.", 
            user.id
        )
        
    await create_audit_log(
        db, 
        "maintenance", 
        record.id, 
        f"WORKFLOW_{action.upper()}", 
        user.id, 
        {"status": old_status}, 
        {
            "status": record.status, 
            "sanction_no": record.sanction_number, 
            "tender_no": record.tender_number, 
            "work_order_no": record.work_order_number, 
            "contractor": record.assigned_contractor
        }
    )
    await db.commit()
    await db.refresh(record)
    return record
