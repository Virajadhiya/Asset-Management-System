from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, func
from app.database import get_db
from app.models.audit import AuditLog
from app.middleware.rbac import require_permission
from app.models.user import User

router = APIRouter()

@router.get("/logs")
async def get_audit_logs(
    page: int = Query(1, ge=1), 
    limit: int = Query(50, ge=1, le=100), 
    entity_type: str = None,
    entity_id: str = None,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_permission("audit", "read"))
):
    offset = (page - 1) * limit
    stmt = select(AuditLog).order_by(desc(AuditLog.timestamp))
    
    if entity_type:
        stmt = stmt.where(AuditLog.entity_type == entity_type)
    if entity_id:
        stmt = stmt.where(AuditLog.entity_id == entity_id)
        
    stmt_page = stmt.offset(offset).limit(limit)
    result = await db.execute(stmt_page)
    items = result.scalars().all()
    
    count_stmt = select(func.count(AuditLog.id))
    if entity_type:
        count_stmt = count_stmt.where(AuditLog.entity_type == entity_type)
    if entity_id:
        count_stmt = count_stmt.where(AuditLog.entity_id == entity_id)
    count_result = await db.execute(count_stmt)
    total = count_result.scalar() or 0
    
    logs = []
    for item in items:
        u_name = "System"
        u_role = None
        if getattr(item, 'user', None):
            u_name = item.user.full_name
            u_role = item.user.role.name if getattr(item.user, 'role', None) else None

        logs.append({
            "id": str(item.id),
            "entity_type": item.entity_type,
            "entity_id": str(item.entity_id),
            "action": item.action,
            "user_id": str(item.user_id) if item.user_id else None,
            "user_name": u_name,
            "user_role": u_role,
            "old_value": item.old_value,
            "new_value": item.new_value,
            "timestamp": item.timestamp.strftime("%Y-%m-%d %H:%M:%S") if item.timestamp else None,
        })
        
    return {"items": logs, "total": total, "page": page, "limit": limit}
