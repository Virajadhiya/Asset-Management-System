import uuid
from datetime import datetime
from sqlalchemy import String, Integer, ForeignKey, DateTime, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models import Base

class Inspection(Base):
    __tablename__ = 'inspections'
    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    bridge_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey('bridges.id'), nullable=False)
    inspector_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey('users.id'), nullable=False)
    inspection_type: Mapped[str] = mapped_column(String, nullable=False)
    status: Mapped[str] = mapped_column(String, nullable=False)
    scheduled_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    completion_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    overall_comments: Mapped[str] = mapped_column(Text, nullable=True)
    weather_condition: Mapped[str] = mapped_column(String, nullable=True)
    overall_condition: Mapped[str] = mapped_column(String, nullable=True)
    findings: Mapped[str] = mapped_column(Text, nullable=True)
    recommendations: Mapped[str] = mapped_column(Text, nullable=True)
    next_inspection_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    
    # Proof of Inspection & Anti-Fraud Verification
    inspector_gps_latitude: Mapped[float] = mapped_column(nullable=True)
    inspector_gps_longitude: Mapped[float] = mapped_column(nullable=True)
    geofence_distance_meters: Mapped[float] = mapped_column(nullable=True)
    geofence_verified: Mapped[bool] = mapped_column(nullable=False, default=True)
    photo_evidence_url: Mapped[str] = mapped_column(String, nullable=True)
    
    # Executive Engineer Quality Audit & Counter-Signature
    counter_signed_by: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey('users.id'), nullable=True)
    counter_signed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    verification_remarks: Mapped[str] = mapped_column(Text, nullable=True)

    bridge: Mapped["Bridge"] = relationship("Bridge", back_populates="inspections")
    inspector: Mapped["User"] = relationship("User", foreign_keys=[inspector_id], lazy="joined")
    verifier_engineer: Mapped["User"] = relationship("User", foreign_keys=[counter_signed_by], lazy="joined")
    components: Mapped[list["InspectionComponent"]] = relationship("InspectionComponent", back_populates="inspection", lazy="joined", cascade="all, delete-orphan")
    defects: Mapped[list["Defect"]] = relationship("Defect", back_populates="inspection", lazy="joined", cascade="all, delete-orphan")
    condition_assessment: Mapped["ConditionAssessment"] = relationship("ConditionAssessment", back_populates="inspection", uselist=False, lazy="selectin")

class InspectionComponent(Base):
    __tablename__ = 'inspection_components'
    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    inspection_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey('inspections.id'), nullable=False)
    component_type: Mapped[str] = mapped_column(String, nullable=False)
    condition_rating: Mapped[int] = mapped_column(Integer, nullable=False)
    notes: Mapped[str] = mapped_column(Text, nullable=True)
    observations: Mapped[str] = mapped_column(Text, nullable=True)
    recommendation: Mapped[str] = mapped_column(Text, nullable=True)
    
    inspection: Mapped["Inspection"] = relationship("Inspection", back_populates="components")

class Defect(Base):
    __tablename__ = 'defects'
    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    inspection_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey('inspections.id'), nullable=False)
    component_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey('inspection_components.id'), nullable=True)
    defect_type: Mapped[str] = mapped_column(String, nullable=False, default="GENERAL")
    severity: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    repair_recommendation: Mapped[str] = mapped_column(Text, nullable=True)
    location_on_bridge: Mapped[str] = mapped_column(String, nullable=True)
    immediate_action_required: Mapped[bool] = mapped_column(nullable=False, default=False)
    status: Mapped[str] = mapped_column(String, nullable=False, default="OPEN")

    inspection: Mapped["Inspection"] = relationship("Inspection", back_populates="defects")
