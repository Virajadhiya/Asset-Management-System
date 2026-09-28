import uuid
from datetime import datetime
from sqlalchemy import String, Float, ForeignKey, DateTime, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models import Base

class ConditionAssessment(Base):
    __tablename__ = 'condition_assessments'
    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    bridge_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey('bridges.id'), nullable=False)
    inspection_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey('inspections.id'), nullable=True)
    structural_score: Mapped[float] = mapped_column(Float, nullable=True, default=75.0)
    functional_score: Mapped[float] = mapped_column(Float, nullable=True, default=80.0)
    safety_score: Mapped[float] = mapped_column(Float, nullable=True, default=70.0)
    health_index_score: Mapped[float] = mapped_column(Float, nullable=False)
    condition_category: Mapped[str] = mapped_column(String, nullable=False)
    calculation_version: Mapped[str] = mapped_column(String, default="prototype-v1", nullable=False)
    assessment_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)

    bridge: Mapped["Bridge"] = relationship("Bridge", back_populates="condition_assessments")
    inspection: Mapped["Inspection"] = relationship("Inspection", back_populates="condition_assessment")

    @property
    def overall_health_index(self) -> float:
        return self.health_index_score
