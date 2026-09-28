import uuid
from typing import List
from sqlalchemy import String, ForeignKey, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models import Base
from app.models.enums import UserRole

class Role(Base):
    __tablename__ = 'roles'
    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    description: Mapped[str] = mapped_column(String, nullable=True)

class Permission(Base):
    __tablename__ = 'permissions'
    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String, unique=True, nullable=False) # e.g., 'bridge:read'

class RolePermission(Base):
    __tablename__ = 'role_permissions'
    role_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey('roles.id'), primary_key=True)
    permission_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey('permissions.id'), primary_key=True)

class User(Base):
    __tablename__ = 'users'
    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    username: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String, nullable=False)
    full_name: Mapped[str] = mapped_column(String, nullable=False)
    email: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    department: Mapped[str] = mapped_column(String, nullable=True)
    role_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey('roles.id'), nullable=False)
    role: Mapped["Role"] = relationship("Role", lazy="joined")
