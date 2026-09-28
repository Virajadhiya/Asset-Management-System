from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models.user import User, RolePermission, Permission
from app.services.auth_service import verify_password, create_access_token
from app.schemas.auth import TokenResponse, UserResponse

router = APIRouter()

@router.post("/login", response_model=TokenResponse)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    stmt = select(User).where(User.username == form_data.username)
    result = await db.execute(stmt)
    user = result.scalars().first()
    
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    # Get permissions
    perm_stmt = select(Permission.name).join(RolePermission).where(
        RolePermission.role_id == user.role_id,
        Permission.id == RolePermission.permission_id
    )
    perm_result = await db.execute(perm_stmt)
    permissions = [row for row in perm_result.scalars().all()]
    
    access_token = create_access_token(data={"sub": str(user.id), "role": user.role.name})
    
    return TokenResponse(
        access_token=access_token,
        user=UserResponse(
            id=str(user.id),
            username=user.username,
            full_name=user.full_name,
            role=user.role.name,
            permissions=permissions
        )
    )
