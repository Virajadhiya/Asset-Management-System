from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    pass

# Import all models for Base.metadata registration in dependency order
from app.models.user import Role, Permission, RolePermission, User
from app.models.bridge import Bridge, BridgeLocation, BridgeEngineering
from app.models.inspection import Inspection, InspectionComponent, Defect
from app.models.condition import ConditionAssessment
from app.models.maintenance import MaintenanceRecord
from app.models.lifecycle import LifecycleEvent
from app.models.audit import AuditLog
from app.models.issue import DistressIssue
