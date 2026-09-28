import uuid
from datetime import datetime
from sqlalchemy import String, ForeignKey, DateTime, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models import Base

class LifecycleEvent(Base):
    __tablename__ = 'lifecycle_events'
    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    bridge_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey('bridges.id'), nullable=False)
    event_type: Mapped[str] = mapped_column(String, nullable=False)
    event_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    previous_status: Mapped[str] = mapped_column(String, nullable=True)
    new_status: Mapped[str] = mapped_column(String, nullable=True)
    remarks: Mapped[str] = mapped_column(Text, nullable=True)
    recorded_by: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey('users.id'), nullable=False)

    bridge: Mapped["Bridge"] = relationship("Bridge", back_populates="lifecycle_events")
    performer: Mapped["User"] = relationship("User", lazy="joined")

    @property
    def event_id(self) -> str:
        return str(self.id)

    @property
    def performed_by_name(self) -> str:
        return self.performer.full_name if self.performer else None
