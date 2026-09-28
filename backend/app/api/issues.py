from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from app.database import get_db
from app.models.issue import DistressIssue
from app.models.bridge import Bridge
from app.models.user import User, Role
from app.schemas.issue import DistressIssueCreate, DistressIssueAssign, DistressIssueResolve
from app.services.audit_service import create_audit_log
from app.middleware.rbac import require_permission
from app.middleware.auth import get_current_user
import uuid
from datetime import datetime

router = APIRouter()

@router.get("")
async def list_issues(
    bridge_id: uuid.UUID = None,
    status: str = None,
    severity: str = None,
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user)
):
    offset = (page - 1) * limit
    stmt = select(DistressIssue).order_by(desc(DistressIssue.created_at))
    
    if bridge_id:
        stmt = stmt.where(DistressIssue.bridge_id == bridge_id)
    if status and status != "ALL":
        stmt = stmt.where(DistressIssue.status == status)
    if severity and severity != "ALL":
        stmt = stmt.where(DistressIssue.severity == severity)
        
    res = await db.execute(stmt.offset(offset).limit(limit))
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
            "reported_by_name": i.reported_by_name or (i.bridge.department if i.bridge else "Citizen Report"),
            "reported_by": str(i.reported_by_id) if i.reported_by_id else None,
            "reporter_name": i.reported_by_name or (i.bridge.department if i.bridge else "Citizen Report"),
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

@router.post("", status_code=status.HTTP_201_CREATED)
async def create_issue(
    data: DistressIssueCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user)
):
    issue_title = data.title or (data.issue_type.replace('_', ' ') if data.issue_type else "Structural Distress")
    
    issue = DistressIssue(
        bridge_id=data.bridge_id,
        title=issue_title,
        description=data.description,
        location_details=data.location_details,
        source=data.source or "FIELD_INSPECTION",
        severity=data.severity or "HIGH",
        photo_url=data.photo_url,
        reported_by_name=data.reported_by_name or user.full_name,
        reported_by_id=user.id,
        status="OPEN"
    )
    db.add(issue)
    await db.commit()
    await db.refresh(issue)
    
    await create_audit_log(
        db, 
        "distress_issue", 
        issue.id, 
        "CREATE", 
        user.id, 
        None, 
        {"title": issue.title, "severity": issue.severity, "source": issue.source}
    )
    return {"id": str(issue.id), "status": issue.status, "title": issue.title}

@router.put("/{id}/assign")
async def assign_issue(
    id: uuid.UUID,
    data: DistressIssueAssign,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_permission("bridge", "update"))
):
    stmt = select(DistressIssue).where(DistressIssue.id == id)
    res = await db.execute(stmt)
    issue = res.scalars().first()
    if not issue:
        raise HTTPException(status_code=404, detail="Distress issue not found")
        
    if data.assigned_inspector_id:
        issue.assigned_inspector_id = data.assigned_inspector_id
    if data.assigned_engineer_id:
        issue.assigned_engineer_id = data.assigned_engineer_id
    if data.target_date:
        issue.target_date = data.target_date
    elif data.target_completion_date:
        try:
            issue.target_date = datetime.strptime(data.target_completion_date, "%Y-%m-%d")
        except Exception:
            pass
            
    issue.status = "ASSIGNED"
    
    await create_audit_log(
        db, 
        "distress_issue", 
        issue.id, 
        "ASSIGN_TASK", 
        user.id, 
        {"status": "OPEN"}, 
        {
            "status": "ASSIGNED", 
            "assigned_inspector_id": str(data.assigned_inspector_id) if data.assigned_inspector_id else None,
            "target_date": issue.target_date.isoformat() if issue.target_date else None
        }
    )
    await db.commit()
    return {"message": "Task successfully assigned to designated engineering officer"}

@router.put("/{id}/resolve")
async def resolve_issue(
    id: uuid.UUID,
    data: DistressIssueResolve,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_permission("bridge", "update"))
):
    stmt = select(DistressIssue).where(DistressIssue.id == id)
    res = await db.execute(stmt)
    issue = res.scalars().first()
    if not issue:
        raise HTTPException(status_code=404, detail="Distress issue not found")
        
    old_status = issue.status
    issue.status = data.status
    if data.status in ("RESOLVED", "CLOSED"):
        issue.resolved_at = datetime.utcnow()
    await create_audit_log(
        db, 
        "distress_issue", 
        issue.id, 
        "RESOLVE", 
        user.id, 
        {"status": old_status}, 
        {"status": data.status, "remarks": data.remarks}
    )
    await db.commit()
    return {"message": f"Issue updated to {data.status}"}

@router.get("/assignable-officers")
async def get_assignable_officers(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user)
):
    # Fetch inspectors
    stmt_insp = (
        select(User)
        .join(Role, User.role_id == Role.id)
        .where(Role.name.in_(["INSPECTOR", "EXECUTIVE_ENGINEER"]))
    )
    res_insp = await db.execute(stmt_insp)
    inspectors = res_insp.scalars().all()
    
    # Fetch engineers
    stmt_eng = (
        select(User)
        .join(Role, User.role_id == Role.id)
        .where(Role.name.in_(["EXECUTIVE_ENGINEER", "DEPARTMENT_HEAD"]))
    )
    res_eng = await db.execute(stmt_eng)
    engineers = res_eng.scalars().all()
    
    return {
        "inspectors": [
            {"id": str(u.id), "full_name": u.full_name, "role": u.role.name if u.role else "INSPECTOR", "department": u.department or "PWD"}
            for u in inspectors
        ],
        "engineers": [
            {"id": str(u.id), "full_name": u.full_name, "role": u.role.name if u.role else "ENGINEER", "department": u.department or "PWD"}
            for u in engineers
        ]
    }
