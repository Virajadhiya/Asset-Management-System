import os

BASE_DIR = r"c:\Users\adhiy\.1\Pravi\backend"

FILES = {
    "requirements.txt": """fastapi==0.115.0
uvicorn[standard]==0.30.0
sqlalchemy[asyncio]==2.0.35
asyncpg==0.30.0
alembic==1.13.0
pydantic==2.9.0
pydantic-settings==2.5.0
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-multipart==0.0.12
httpx==0.27.0
geoalchemy2==0.15.0
greenlet==3.1.0
pytest==8.3.0
pytest-asyncio==0.24.0
""",
    ".env.example": """DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/pravi
SECRET_KEY=dev-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=480
CORS_ORIGINS=http://localhost:5173
""",
    "Dockerfile": """FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
""",
    "app/__init__.py": "",
    "app/config.py": """from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/pravi"
    SECRET_KEY: str = "dev-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 480
    CORS_ORIGINS: str = "http://localhost:5173"

    model_config = SettingsConfigDict(env_file=".env")

settings = Settings()
""",
    "app/database.py": """from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from app.config import settings

engine = create_async_engine(settings.DATABASE_URL, echo=False)
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
""",
    "app/main.py": """from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.api.router import api_router
from app.config import settings
from app.database import engine
from app.models import enums, bridge, inspection, condition, maintenance, lifecycle, user, audit

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Base = user.Base # Note: imported all models to ensure they are registered
    # async with engine.begin() as conn:
    #     await conn.run_sync(Base.metadata.create_all)
    yield

app = FastAPI(title="PRAVI Backend", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in settings.CORS_ORIGINS.split(",")],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api")

@app.get("/")
async def root():
    return {"message": "PRAVI Bridge Platform API"}
""",
    "app/models/__init__.py": """from sqlalchemy.orm import DeclarativeBase
class Base(DeclarativeBase):
    pass
""",
    "app/models/enums.py": """import enum

class BridgeType(str, enum.Enum):
    BEAM = "BEAM"
    ARCH = "ARCH"
    TRUSS = "TRUSS"
    SLAB = "SLAB"
    SUSPENSION = "SUSPENSION"
    CABLE_STAYED = "CABLE_STAYED"
    CANTILEVER = "CANTILEVER"
    BOX_GIRDER = "BOX_GIRDER"
    OTHER = "OTHER"

class StructureCategory(str, enum.Enum):
    CULVERT = "CULVERT"
    MINOR = "MINOR"
    MAJOR = "MAJOR"
    EXTRA_LONG = "EXTRA_LONG"

class BridgeStatus(str, enum.Enum):
    PLANNED = "PLANNED"
    UNDER_CONSTRUCTION = "UNDER_CONSTRUCTION"
    OPERATIONAL = "OPERATIONAL"
    UNDER_MAINTENANCE = "UNDER_MAINTENANCE"
    UNDER_REHABILITATION = "UNDER_REHABILITATION"
    CLOSED = "CLOSED"
    DECOMMISSIONED = "DECOMMISSIONED"

class InspectionType(str, enum.Enum):
    ROUTINE = "ROUTINE"
    PRINCIPAL = "PRINCIPAL"
    EMERGENT = "EMERGENT"
    UNDERWATER = "UNDERWATER"
    SPECIAL = "SPECIAL"

class InspectionStatus(str, enum.Enum):
    SCHEDULED = "SCHEDULED"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"

class ComponentType(str, enum.Enum):
    DECK = "DECK"
    SUPERSTRUCTURE = "SUPERSTRUCTURE"
    SUBSTRUCTURE = "SUBSTRUCTURE"
    FOUNDATION = "FOUNDATION"
    BEARINGS = "BEARINGS"
    EXPANSION_JOINTS = "EXPANSION_JOINTS"
    APPROACHES = "APPROACHES"
    DRAINAGE = "DRAINAGE"
    SAFETY_BARRIERS = "SAFETY_BARRIERS"
    SCOUR_RIVERBED = "SCOUR_RIVERBED"
    WATERWAY = "WATERWAY"

class ConditionCategory(str, enum.Enum):
    EXCELLENT = "EXCELLENT"
    GOOD = "GOOD"
    FAIR = "FAIR"
    POOR = "POOR"
    CRITICAL = "CRITICAL"

class DefectSeverity(str, enum.Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"

class MaintenanceType(str, enum.Enum):
    ROUTINE = "ROUTINE"
    PREVENTIVE = "PREVENTIVE"
    REPAIR = "REPAIR"
    REHABILITATION = "REHABILITATION"
    STRENGTHENING = "STRENGTHENING"
    EMERGENCY_REPAIR = "EMERGENCY_REPAIR"
    RECONSTRUCTION = "RECONSTRUCTION"

class MaintenancePriority(str, enum.Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"

class MaintenanceStatus(str, enum.Enum):
    REPORTED = "REPORTED"
    APPROVED = "APPROVED"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    VERIFIED = "VERIFIED"
    CANCELLED = "CANCELLED"

class LifecycleEventType(str, enum.Enum):
    PROPOSED = "PROPOSED"
    SURVEYED = "SURVEYED"
    DESIGNED = "DESIGNED"
    APPROVED = "APPROVED"
    TENDERED = "TENDERED"
    CONSTRUCTION_STARTED = "CONSTRUCTION_STARTED"
    CONSTRUCTION_COMPLETED = "CONSTRUCTION_COMPLETED"
    COMMISSIONED = "COMMISSIONED"
    INSPECTION_COMPLETED = "INSPECTION_COMPLETED"
    MAINTENANCE_STARTED = "MAINTENANCE_STARTED"
    MAINTENANCE_COMPLETED = "MAINTENANCE_COMPLETED"
    REPAIR_STARTED = "REPAIR_STARTED"
    REPAIR_COMPLETED = "REPAIR_COMPLETED"
    REHABILITATION_STARTED = "REHABILITATION_STARTED"
    REHABILITATION_COMPLETED = "REHABILITATION_COMPLETED"
    CLOSED = "CLOSED"
    REOPENED = "REOPENED"
    DECOMMISSIONED = "DECOMMISSIONED"

class DocumentType(str, enum.Enum):
    DESIGN_DRAWING = "DESIGN_DRAWING"
    STRUCTURAL_DRAWING = "STRUCTURAL_DRAWING"
    INSPECTION_REPORT = "INSPECTION_REPORT"
    MAINTENANCE_REPORT = "MAINTENANCE_REPORT"
    CONTRACT = "CONTRACT"
    CERTIFICATE = "CERTIFICATE"
    PHOTOGRAPH = "PHOTOGRAPH"
    VIDEO = "VIDEO"
    OTHER = "OTHER"

class UserRole(str, enum.Enum):
    ADMIN = "ADMIN"
    DEPARTMENT_HEAD = "DEPARTMENT_HEAD"
    EXECUTIVE_ENGINEER = "EXECUTIVE_ENGINEER"
    INSPECTOR = "INSPECTOR"
    MAINTENANCE_OFFICER = "MAINTENANCE_OFFICER"
    VIEWER = "VIEWER"

class OperationalStatus(str, enum.Enum):
    OPERATIONAL = "OPERATIONAL"
    PARTIALLY_CLOSED = "PARTIALLY_CLOSED"
    CLOSED = "CLOSED"
    UNDER_MAINTENANCE = "UNDER_MAINTENANCE"
    UNDER_REHABILITATION = "UNDER_REHABILITATION"
""",
    "app/models/user.py": """import uuid
from typing import List
from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from app.models import Base
from app.models.enums import UserRole

class Role(Base):
    __tablename__ = 'roles'
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    description: Mapped[str] = mapped_column(String, nullable=True)

class Permission(Base):
    __tablename__ = 'permissions'
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String, unique=True, nullable=False) # e.g., 'bridge:read'

class RolePermission(Base):
    __tablename__ = 'role_permissions'
    role_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey('roles.id'), primary_key=True)
    permission_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey('permissions.id'), primary_key=True)

class User(Base):
    __tablename__ = 'users'
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String, nullable=False)
    full_name: Mapped[str] = mapped_column(String, nullable=False)
    email: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    role_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey('roles.id'), nullable=False)
    role: Mapped["Role"] = relationship("Role", lazy="joined")
""",
    "app/models/bridge.py": """import uuid
from datetime import datetime
from sqlalchemy import String, Integer, Float, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from app.models import Base
from app.models.enums import BridgeType, StructureCategory, BridgeStatus, OperationalStatus

class Bridge(Base):
    __tablename__ = 'bridges'
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    bridge_id_str: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String, nullable=False)
    bridge_type: Mapped[str] = mapped_column(String, nullable=False) # Store Enum as VARCHAR
    structure_category: Mapped[str] = mapped_column(String, nullable=False)
    current_status: Mapped[str] = mapped_column(String, nullable=False)
    
    # Ownership merged
    department: Mapped[str] = mapped_column(String, nullable=True)
    owning_authority: Mapped[str] = mapped_column(String, nullable=True)
    maintaining_authority: Mapped[str] = mapped_column(String, nullable=True)
    responsible_officer_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=True)
    
    # Operations merged
    traffic_status: Mapped[str] = mapped_column(String, nullable=True)
    daily_traffic_estimate: Mapped[int] = mapped_column(Integer, nullable=True)
    load_restriction: Mapped[float] = mapped_column(Float, nullable=True)
    speed_restriction: Mapped[float] = mapped_column(Float, nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    location: Mapped["BridgeLocation"] = relationship("BridgeLocation", back_populates="bridge", uselist=False, lazy="joined")
    engineering: Mapped["BridgeEngineering"] = relationship("BridgeEngineering", back_populates="bridge", uselist=False, lazy="joined")

class BridgeLocation(Base):
    __tablename__ = 'bridge_locations'
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    bridge_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey('bridges.id'), unique=True, nullable=False)
    latitude: Mapped[float] = mapped_column(Float, nullable=False)
    longitude: Mapped[float] = mapped_column(Float, nullable=False)
    district: Mapped[str] = mapped_column(String, nullable=False)
    state: Mapped[str] = mapped_column(String, nullable=False)
    river_crossing: Mapped[str] = mapped_column(String, nullable=True)
    road_name: Mapped[str] = mapped_column(String, nullable=True)

    bridge: Mapped["Bridge"] = relationship("Bridge", back_populates="location")

class BridgeEngineering(Base):
    __tablename__ = 'bridge_engineering'
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    bridge_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey('bridges.id'), unique=True, nullable=False)
    total_length: Mapped[float] = mapped_column(Float, nullable=True)
    number_of_spans: Mapped[int] = mapped_column(Integer, nullable=True)
    deck_width: Mapped[float] = mapped_column(Float, nullable=True)
    design_life: Mapped[int] = mapped_column(Integer, nullable=True, default=100)
    year_built: Mapped[int] = mapped_column(Integer, nullable=True)
    
    bridge: Mapped["Bridge"] = relationship("Bridge", back_populates="engineering")
""",
    "app/models/inspection.py": """import uuid
from datetime import datetime
from sqlalchemy import String, Integer, ForeignKey, DateTime, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from app.models import Base

class Inspection(Base):
    __tablename__ = 'inspections'
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    bridge_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey('bridges.id'), nullable=False)
    inspector_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    inspection_type: Mapped[str] = mapped_column(String, nullable=False)
    status: Mapped[str] = mapped_column(String, nullable=False)
    scheduled_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    completion_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    overall_comments: Mapped[str] = mapped_column(Text, nullable=True)

    components: Mapped[list["InspectionComponent"]] = relationship("InspectionComponent", back_populates="inspection", lazy="joined")
    defects: Mapped[list["Defect"]] = relationship("Defect", back_populates="inspection", lazy="joined")

class InspectionComponent(Base):
    __tablename__ = 'inspection_components'
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    inspection_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey('inspections.id'), nullable=False)
    component_type: Mapped[str] = mapped_column(String, nullable=False)
    condition_rating: Mapped[int] = mapped_column(Integer, nullable=False)
    notes: Mapped[str] = mapped_column(Text, nullable=True)
    
    inspection: Mapped["Inspection"] = relationship("Inspection", back_populates="components")

class Defect(Base):
    __tablename__ = 'defects'
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    inspection_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey('inspections.id'), nullable=False)
    component_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey('inspection_components.id'), nullable=True)
    severity: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    repair_recommendation: Mapped[str] = mapped_column(Text, nullable=True)

    inspection: Mapped["Inspection"] = relationship("Inspection", back_populates="defects")
""",
    "app/models/condition.py": """import uuid
from datetime import datetime
from sqlalchemy import String, Float, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from app.models import Base

class ConditionAssessment(Base):
    __tablename__ = 'condition_assessments'
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    bridge_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey('bridges.id'), nullable=False)
    inspection_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey('inspections.id'), nullable=False)
    health_index_score: Mapped[float] = mapped_column(Float, nullable=False)
    condition_category: Mapped[str] = mapped_column(String, nullable=False)
    calculation_version: Mapped[str] = mapped_column(String, default="prototype-v1", nullable=False)
    assessment_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
""",
    "app/models/maintenance.py": """import uuid
from datetime import datetime
from sqlalchemy import String, Float, ForeignKey, DateTime, Text
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID
from app.models import Base

class MaintenanceRecord(Base):
    __tablename__ = 'maintenance_records'
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    bridge_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey('bridges.id'), nullable=False)
    maintenance_type: Mapped[str] = mapped_column(String, nullable=False)
    priority: Mapped[str] = mapped_column(String, nullable=False)
    status: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    estimated_cost: Mapped[float] = mapped_column(Float, nullable=True)
    actual_cost: Mapped[float] = mapped_column(Float, nullable=True)
    contractor_name: Mapped[str] = mapped_column(String, nullable=True)
    start_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    completion_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    approved_by: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=True)
""",
    "app/models/lifecycle.py": """import uuid
from datetime import datetime
from sqlalchemy import String, ForeignKey, DateTime, Text
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID
from app.models import Base

class LifecycleEvent(Base):
    __tablename__ = 'lifecycle_events'
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    bridge_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey('bridges.id'), nullable=False)
    event_type: Mapped[str] = mapped_column(String, nullable=False)
    event_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    previous_status: Mapped[str] = mapped_column(String, nullable=True)
    new_status: Mapped[str] = mapped_column(String, nullable=True)
    recorded_by: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
""",
    "app/models/audit.py": """import uuid
from datetime import datetime
from sqlalchemy import String, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID, JSONB
from app.models import Base

class AuditLog(Base):
    __tablename__ = 'audit_logs'
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    entity_type: Mapped[str] = mapped_column(String, nullable=False)
    entity_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    action: Mapped[str] = mapped_column(String, nullable=False) # CREATE, UPDATE, DELETE
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=True)
    old_value = mapped_column(JSONB, nullable=True)
    new_value = mapped_column(JSONB, nullable=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
""",
    "app/schemas/__init__.py": "",
    "app/schemas/common.py": """from pydantic import BaseModel
from typing import Generic, TypeVar, List, Optional
from pydantic import ConfigDict

T = TypeVar('T')

class PaginatedResponse(BaseModel, Generic[T]):
    items: List[T]
    total: int
    page: int
    limit: int
""",
    "app/schemas/auth.py": """from pydantic import BaseModel
from typing import List

class LoginRequest(BaseModel):
    username: str
    password: str

class UserResponse(BaseModel):
    id: str
    username: str
    full_name: str
    role: str
    permissions: List[str]

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse
""",
    "app/schemas/bridge.py": """from pydantic import BaseModel
from typing import Optional
from uuid import UUID

class BridgeLocationBase(BaseModel):
    latitude: float
    longitude: float
    district: str
    state: str
    river_crossing: Optional[str] = None
    road_name: Optional[str] = None

class BridgeEngineeringBase(BaseModel):
    total_length: Optional[float] = None
    number_of_spans: Optional[int] = None
    deck_width: Optional[float] = None
    design_life: Optional[int] = 100
    year_built: Optional[int] = None

class BridgeCreate(BaseModel):
    bridge_id_str: str
    name: str
    bridge_type: str
    structure_category: str
    current_status: str
    department: Optional[str] = None
    owning_authority: Optional[str] = None
    maintaining_authority: Optional[str] = None
    traffic_status: Optional[str] = None
    location: BridgeLocationBase
    engineering: BridgeEngineeringBase

class BridgeUpdate(BaseModel):
    name: Optional[str] = None
    bridge_type: Optional[str] = None
    structure_category: Optional[str] = None
    department: Optional[str] = None
    # current_status MUST NOT be updated via this endpoint

class BridgeListItem(BaseModel):
    id: UUID
    bridge_id_str: str
    name: str
    bridge_type: str
    current_status: str
    district: Optional[str] = None
    latest_health_index: Optional[float] = None

class BridgeResponse(BridgeCreate):
    id: UUID
    location: BridgeLocationBase
    engineering: BridgeEngineeringBase
""",
    "app/schemas/inspection.py": """from pydantic import BaseModel
from typing import List, Optional
from uuid import UUID
from datetime import datetime

class ComponentCreate(BaseModel):
    component_type: str
    condition_rating: int
    notes: Optional[str] = None

class DefectCreate(BaseModel):
    severity: str
    description: str
    component_id: Optional[UUID] = None

class InspectionCreate(BaseModel):
    inspection_type: str
    scheduled_date: Optional[datetime] = None
    components: List[ComponentCreate] = []
    defects: List[DefectCreate] = []
""",
    "app/schemas/maintenance.py": """from pydantic import BaseModel
from typing import Optional
from uuid import UUID

class MaintenanceCreate(BaseModel):
    maintenance_type: str
    priority: str
    description: Optional[str] = None
    estimated_cost: Optional[float] = None

class MaintenanceStatusUpdate(BaseModel):
    action: str # approve, start, complete, verify
""",
    "app/schemas/lifecycle.py": """from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from uuid import UUID

class LifecycleEventCreate(BaseModel):
    event_type: str
    event_date: datetime
    description: Optional[str] = None
""",
    "app/schemas/dashboard.py": """from pydantic import BaseModel
from typing import Dict

class DashboardSummaryResponse(BaseModel):
    total_bridges: int
    by_status: Dict[str, int]
    by_condition: Dict[str, int]
    critical_count: int
    overdue_inspections: int
""",
    "app/middleware/__init__.py": "",
    "app/middleware/auth.py": """from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from app.config import settings
from app.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.user import User
from uuid import UUID

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login")

async def get_current_user(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    stmt = select(User).where(User.id == UUID(user_id))
    result = await db.execute(stmt)
    user = result.scalars().first()
    if user is None:
        raise credentials_exception
    return user
""",
    "app/middleware/rbac.py": """from fastapi import Depends, HTTPException, status
from app.middleware.auth import get_current_user
from app.models.user import User
from app.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.user import RolePermission, Permission

def require_permission(resource: str, action: str):
    async def permission_checker(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
        perm_str = f"{resource}:{action}"
        
        stmt = select(Permission.name).join(RolePermission).where(
            RolePermission.role_id == current_user.role_id,
            Permission.id == RolePermission.permission_id
        )
        result = await db.execute(stmt)
        perms = [row for row in result.scalars().all()]
        
        if perm_str not in perms:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
        return current_user
    return permission_checker
""",
    "app/services/__init__.py": "",
    "app/services/auth_service.py": """from passlib.context import CryptContext
from datetime import datetime, timedelta
from jose import jwt
from app.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt
""",
    "app/services/bridge_service.py": """# Implementation placeholder
""",
    "app/services/inspection_service.py": """# Implementation placeholder
""",
    "app/services/health_index.py": """def calculate_bhi(components: list, design_life: int = 100, age: int = 0) -> float:
    # Prototype v1 calculation
    structural = 80 # Placeholder
    functional = 80
    safety = 70
    age_factor = max(0, 100 - (age / design_life * 100))
    bhi = 0.40 * structural + 0.30 * functional + 0.20 * safety + 0.10 * age_factor
    return bhi
""",
    "app/services/lifecycle_service.py": """# State Machine
VALID_TRANSITIONS = {
    'PLANNED': ['UNDER_CONSTRUCTION'],
    'UNDER_CONSTRUCTION': ['OPERATIONAL'],
    'OPERATIONAL': ['UNDER_MAINTENANCE', 'UNDER_REHABILITATION', 'CLOSED', 'DECOMMISSIONED'],
    'UNDER_MAINTENANCE': ['OPERATIONAL', 'CLOSED'],
    'UNDER_REHABILITATION': ['OPERATIONAL', 'CLOSED'],
    'CLOSED': ['OPERATIONAL', 'DECOMMISSIONED'],
    'DECOMMISSIONED': [],
}

EVENT_TO_NEW_STATUS = {
    'CONSTRUCTION_STARTED': 'UNDER_CONSTRUCTION',
    'COMMISSIONED': 'OPERATIONAL',
    'MAINTENANCE_STARTED': 'UNDER_MAINTENANCE',
    'MAINTENANCE_COMPLETED': 'OPERATIONAL',
    'REHABILITATION_STARTED': 'UNDER_REHABILITATION',
    'REHABILITATION_COMPLETED': 'OPERATIONAL',
    'CLOSED': 'CLOSED',
    'REOPENED': 'OPERATIONAL',
    'DECOMMISSIONED': 'DECOMMISSIONED',
}

async def process_lifecycle_event(bridge, event_type, db_session):
    # Process event and update bridge status safely
    pass
""",
    "app/services/maintenance_service.py": """# Implementation placeholder
""",
    "app/services/dashboard_service.py": """# Implementation placeholder
""",
    "app/services/audit_service.py": """async def create_audit_log(db_session, entity_type, entity_id, action, user_id, old_val, new_val):
    from app.models.audit import AuditLog
    log = AuditLog(entity_type=entity_type, entity_id=entity_id, action=action, user_id=user_id, old_value=old_val, new_value=new_val)
    db_session.add(log)
""",
    "app/api/__init__.py": "",
    "app/api/router.py": """from fastapi import APIRouter
from app.api import auth, bridges, inspections, maintenance, lifecycle, dashboard, gis, audit

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(bridges.router, prefix="/bridges", tags=["bridges"])
api_router.include_router(inspections.router, prefix="/inspections", tags=["inspections"])
api_router.include_router(maintenance.router, prefix="/maintenance", tags=["maintenance"])
api_router.include_router(lifecycle.router, prefix="/lifecycle", tags=["lifecycle"])
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["dashboard"])
api_router.include_router(gis.router, prefix="/gis", tags=["gis"])
api_router.include_router(audit.router, prefix="/audit", tags=["audit"])
""",
    "app/api/auth.py": """from fastapi import APIRouter
router = APIRouter()
""",
    "app/api/bridges.py": """from fastapi import APIRouter
router = APIRouter()
""",
    "app/api/inspections.py": """from fastapi import APIRouter
router = APIRouter()
""",
    "app/api/maintenance.py": """from fastapi import APIRouter
router = APIRouter()
""",
    "app/api/lifecycle.py": """from fastapi import APIRouter
router = APIRouter()
""",
    "app/api/dashboard.py": """from fastapi import APIRouter
router = APIRouter()
""",
    "app/api/gis.py": """from fastapi import APIRouter
router = APIRouter()
""",
    "app/api/audit.py": """from fastapi import APIRouter
router = APIRouter()
""",
    "app/seed/__init__.py": "",
    "app/seed/seed_data.py": """import asyncio
from app.database import engine, AsyncSessionLocal
from app.models import Base
# Full seed logic goes here

async def main():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("Database seeded successfully.")

if __name__ == "__main__":
    asyncio.run(main())
"""
}

for path, content in FILES.items():
    full_path = os.path.join(BASE_DIR, path)
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    with open(full_path, "w", encoding="utf-8") as f:
        f.write(content)

print("Backend foundation generated.")
