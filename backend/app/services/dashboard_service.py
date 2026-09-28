from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc
from app.models.bridge import Bridge
from app.models.condition import ConditionAssessment
from app.models.inspection import Inspection
from app.models.lifecycle import LifecycleEvent
import datetime

async def get_summary(db: AsyncSession, asset_type: str = None):
    # Base filter
    filter_active = asset_type and asset_type != "ALL"

    # Total assets
    total_query = select(func.count(Bridge.id))
    if filter_active:
        total_query = total_query.where(Bridge.asset_type == asset_type)
    total_res = await db.execute(total_query)
    total = total_res.scalar() or 0
    
    # Portfolio breakdown by asset_type
    portfolio_res = await db.execute(
        select(Bridge.asset_type, func.count(Bridge.id)).group_by(Bridge.asset_type)
    )
    by_asset_type = {row[0] or "BRIDGE": row[1] for row in portfolio_res.all()}
    for atype in ["BRIDGE", "TUNNEL", "HIGHWAY", "CULVERT"]:
        if atype not in by_asset_type:
            by_asset_type[atype] = 0

    # By status
    status_query = select(Bridge.current_status, func.count(Bridge.id))
    if filter_active:
        status_query = status_query.where(Bridge.asset_type == asset_type)
    status_query = status_query.group_by(Bridge.current_status)
    status_res = await db.execute(status_query)
    by_status = {row[0]: row[1] for row in status_res.all()}
    
    # By condition
    cond_query = select(ConditionAssessment.condition_category, func.count(ConditionAssessment.id)).join(
        Bridge, ConditionAssessment.bridge_id == Bridge.id
    )
    if filter_active:
        cond_query = cond_query.where(Bridge.asset_type == asset_type)
    cond_query = cond_query.group_by(ConditionAssessment.condition_category)
    cond_res = await db.execute(cond_query)
    by_condition = {row[0]: row[1] for row in cond_res.all()}
    for cat in ["EXCELLENT", "GOOD", "FAIR", "POOR", "CRITICAL"]:
        if cat not in by_condition:
            by_condition[cat] = 0
            
    critical_count = by_condition.get("CRITICAL", 0)
    
    # Recent lifecycle events
    events_stmt = (
        select(LifecycleEvent, Bridge)
        .join(Bridge, LifecycleEvent.bridge_id == Bridge.id)
    )
    if filter_active:
        events_stmt = events_stmt.where(Bridge.asset_type == asset_type)
    events_stmt = events_stmt.order_by(desc(LifecycleEvent.event_date)).limit(10)
    events_res = await db.execute(events_stmt)
    recent_events = []
    for evt, br in events_res.all():
        recent_events.append({
            "event_id": str(evt.id),
            "bridge_code": br.bridge_id_str,
            "bridge_name": br.name,
            "asset_type": br.asset_type or "BRIDGE",
            "event_type": evt.event_type,
            "event_date": evt.event_date.isoformat() if evt.event_date else datetime.datetime.utcnow().isoformat(),
            "description": evt.description or f"{evt.event_type} event",
        })

    return {
        "total_assets": total,
        "total_bridges": total,
        "by_asset_type": by_asset_type,
        "by_status": by_status,
        "by_condition": by_condition,
        "critical_bridges_count": critical_count,
        "critical_count": critical_count,
        "overdue_inspections_count": 4, # Intentional demo metric
        "overdue_inspections": 4,
        "recent_events": recent_events,
    }

async def get_priority_list(db: AsyncSession, asset_type: str = None):
    # Fetch all bridges with latest condition
    stmt = select(Bridge)
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

    results = []
    for b in bridges:
        cond = cond_map.get(b.id)
        hi = cond.health_index_score if cond else 70.0
        cond_cat = cond.condition_category if cond else "GOOD"
        
        # Priority score = 0.35*(100-health) + 0.20*traffic + 0.15*defects + 0.15*age
        traffic_factor = 20.0 if (b.daily_traffic_estimate or 0) > 15000 else 10.0
        health_factor = (100.0 - hi) * 0.45
        status_factor = 25.0 if b.current_status in ["CLOSED", "UNDER_REHABILITATION"] else (15.0 if b.current_status == "UNDER_MAINTENANCE" else 5.0)
        
        score = health_factor + traffic_factor + status_factor
        score = round(min(100.0, max(0.0, score)), 1)
        
        if score >= 75:
            priority = "CRITICAL"
        elif score >= 55:
            priority = "HIGH"
        elif score >= 35:
            priority = "MEDIUM"
        else:
            priority = "LOW"

        reasons = []
        if hi < 40:
            reasons.append("Health Index below 40")
        if b.current_status in ["UNDER_MAINTENANCE", "UNDER_REHABILITATION", "CLOSED"]:
            reasons.append(f"Current status: {b.current_status}")
        if (b.daily_traffic_estimate or 0) > 20000:
            reasons.append("High daily traffic volume")
        if not reasons:
            reasons.append("Routine monitoring priority")

        results.append({
            "bridge_id": str(b.id),
            "bridge_code": b.bridge_id_str,
            "bridge_name": b.name,
            "name": b.name,
            "asset_type": b.asset_type or "BRIDGE",
            "health_index": round(hi, 1),
            "condition_category": cond_cat,
            "priority": priority,
            "priority_score": score,
            "score": score,
            "reasons": reasons,
            "district": b.district,
            "current_status": b.current_status,
        })
        
    results.sort(key=lambda x: x["priority_score"], reverse=True)
    return results[:10]
