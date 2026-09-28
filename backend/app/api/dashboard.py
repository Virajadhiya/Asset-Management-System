from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.services.dashboard_service import get_summary, get_priority_list
from app.middleware.rbac import require_permission
from app.models.user import User

router = APIRouter()

@router.get("/summary")
async def get_dashboard_summary(
    asset_type: str = None,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_permission("bridge", "read"))
):
    return await get_summary(db, asset_type)

@router.get("/priority-list")
async def get_dashboard_priority_list(
    asset_type: str = None,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_permission("bridge", "read"))
):
    return await get_priority_list(db, asset_type)
