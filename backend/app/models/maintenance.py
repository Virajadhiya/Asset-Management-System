import uuid
from datetime import datetime
from sqlalchemy import String, Float, ForeignKey, DateTime, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models import Base

class MaintenanceRecord(Base):
    __tablename__ = 'maintenance_records'
    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    bridge_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey('bridges.id'), nullable=False)
    maintenance_type: Mapped[str] = mapped_column(String, nullable=False)
    priority: Mapped[str] = mapped_column(String, nullable=False)
    status: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    estimated_cost: Mapped[float] = mapped_column(Float, nullable=True)
    estimated_by: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey('users.id'), nullable=True)
    actual_cost: Mapped[float] = mapped_column(Float, nullable=True)
    
    # Government Administrative & Financial Sanction
    sanction_number: Mapped[str] = mapped_column(String, nullable=True) # e.g. AA/R&B/2026/089
    sanctioned_amount: Mapped[float] = mapped_column(Float, nullable=True)
    
    # Tendering & Procurement
    tender_number: Mapped[str] = mapped_column(String, nullable=True) # e.g. NIT/GJ/2026/BR-402
    work_order_number: Mapped[str] = mapped_column(String, nullable=True) # e.g. WO/R&B/2026/1102
    tender_value: Mapped[float] = mapped_column(Float, nullable=True)
    contractor_name: Mapped[str] = mapped_column(String, nullable=True)
    assigned_contractor: Mapped[str] = mapped_column(String, nullable=True)

    reported_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    start_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    completion_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    approved_by: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey('users.id'), nullable=True)
    verified_by: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey('users.id'), nullable=True)

    bridge: Mapped["Bridge"] = relationship("Bridge", back_populates="maintenance_records")
    estimator: Mapped["User"] = relationship("User", foreign_keys=[estimated_by], lazy="joined")
    approver: Mapped["User"] = relationship("User", foreign_keys=[approved_by], lazy="joined")
    verifier: Mapped["User"] = relationship("User", foreign_keys=[verified_by], lazy="joined")

    @property
    def maintenance_id(self) -> str:
        return str(self.id)

    @property
    def issue_description(self) -> str:
        return self.description or ""
