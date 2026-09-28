from datetime import datetime
from app.models.audit import AuditLog

async def create_audit_log(db_session, entity_type: str, entity_id, action: str, user_id, old_val: dict, new_val: dict, ip_address: str = None, remarks: str = None):
    log = AuditLog(
        entity_type=entity_type,
        entity_id=entity_id,
        action=action,
        user_id=user_id,
        old_value=old_val,
        new_value=new_val,
        timestamp=datetime.utcnow()
    )
    db_session.add(log)
    await db_session.commit()
    await db_session.refresh(log)
    return log
