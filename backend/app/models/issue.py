import uuid
from datetime import datetime
from sqlalchemy import String, ForeignKey, DateTime, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models import Base

class DistressIssue(Base):
    __tablename__ = 'distress_issues'
    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    bridge_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey('bridges.id'), nullable=False)
    title: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    location_details: Mapped[str] = mapped_column(String, nullable=True)
    source: Mapped[str] = mapped_column(String, nullable=False, default="FIELD_SCOUT") # FIELD_SCOUT, PUBLIC_GRIEVANCE, POLICE_ALERT, INSPECTION
    severity: Mapped[str] = mapped_column(String, nullable=False, default="HIGH") # CRITICAL, HIGH, MEDIUM, LOW
    photo_url: Mapped[str] = mapped_column(String, nullable=True)
    status: Mapped[str] = mapped_column(String, nullable=False, default="OPEN") # OPEN, ASSIGNED, IN_PROGRESS, RESOLVED
    
    # Task assignment
    assigned_inspector_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey('users.id'), nullable=True)
    assigned_engineer_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey('users.id'), nullable=True)
    target_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    
    # Reporter
    reported_by_name: Mapped[str] = mapped_column(String, nullable=True)
    reported_by_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey('users.id'), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    resolved_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)

    bridge: Mapped["Bridge"] = relationship("Bridge", lazy="joined")
    assigned_inspector: Mapped["User"] = relationship("User", foreign_keys=[assigned_inspector_id], lazy="joined")
    assigned_engineer: Mapped["User"] = relationship("User", foreign_keys=[assigned_engineer_id], lazy="joined")
