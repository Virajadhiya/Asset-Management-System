import uuid
from datetime import datetime
from sqlalchemy import String, ForeignKey, DateTime, Uuid, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models import Base

class AuditLog(Base):
    __tablename__ = 'audit_logs'
    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    entity_type: Mapped[str] = mapped_column(String, nullable=False)
    entity_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    action: Mapped[str] = mapped_column(String, nullable=False) # CREATE, UPDATE, DELETE
    user_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey('users.id'), nullable=True)
    old_value = mapped_column(JSON, nullable=True)
    new_value = mapped_column(JSON, nullable=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)

    user: Mapped["User"] = relationship("User", lazy="joined")
