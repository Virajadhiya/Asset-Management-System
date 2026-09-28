from fastapi import Depends, HTTPException, status
from app.middleware.auth import get_current_user
from app.models.user import User, RolePermission, Permission
from app.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

def require_permission(resource: str, action: str):
    async def permission_checker(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
        # Admin has superuser access to all resources
        if current_user.role and current_user.role.name == "ADMIN":
            return current_user
            
        perm_str = f"{resource}:{action}"
        
        stmt = (
            select(Permission.name)
            .join(RolePermission, Permission.id == RolePermission.permission_id)
            .where(RolePermission.role_id == current_user.role_id)
        )
        result = await db.execute(stmt)
        perms = [row for row in result.scalars().all()]
        
        if perm_str not in perms:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, 
                detail=f"Not authorized. Requires permission: {perm_str}"
            )
        return current_user
    return permission_checker
