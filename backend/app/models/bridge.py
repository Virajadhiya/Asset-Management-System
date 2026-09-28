import uuid
from datetime import datetime
from sqlalchemy import String, Integer, Float, ForeignKey, DateTime, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models import Base
from app.models.enums import BridgeType, StructureCategory, BridgeStatus, OperationalStatus

class Bridge(Base):
    __tablename__ = 'bridges'
    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    bridge_id_str: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String, nullable=False)
    asset_type: Mapped[str] = mapped_column(String, nullable=False, default="BRIDGE") # BRIDGE, TUNNEL, HIGHWAY, CULVERT
    bridge_type: Mapped[str] = mapped_column(String, nullable=False) # Store Enum as VARCHAR
    structure_category: Mapped[str] = mapped_column(String, nullable=False)
    current_status: Mapped[str] = mapped_column(String, nullable=False)
    
    # Ownership merged
    department: Mapped[str] = mapped_column(String, nullable=True)
    owning_authority: Mapped[str] = mapped_column(String, nullable=True)
    maintaining_authority: Mapped[str] = mapped_column(String, nullable=True)
    responsible_officer_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey('users.id'), nullable=True)
    
    # Operations merged
    traffic_status: Mapped[str] = mapped_column(String, nullable=True)
    daily_traffic_estimate: Mapped[int] = mapped_column(Integer, nullable=True)
    load_restriction: Mapped[float] = mapped_column(Float, nullable=True)
    speed_restriction: Mapped[float] = mapped_column(Float, nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    location: Mapped["BridgeLocation"] = relationship("BridgeLocation", back_populates="bridge", uselist=False, lazy="joined", cascade="all, delete-orphan")
    engineering: Mapped["BridgeEngineering"] = relationship("BridgeEngineering", back_populates="bridge", uselist=False, lazy="joined", cascade="all, delete-orphan")
    inspections: Mapped[list["Inspection"]] = relationship("Inspection", back_populates="bridge", lazy="selectin", cascade="all, delete-orphan")
    condition_assessments: Mapped[list["ConditionAssessment"]] = relationship("ConditionAssessment", back_populates="bridge", lazy="selectin", cascade="all, delete-orphan")
    maintenance_records: Mapped[list["MaintenanceRecord"]] = relationship("MaintenanceRecord", back_populates="bridge", lazy="selectin", cascade="all, delete-orphan")
    lifecycle_events: Mapped[list["LifecycleEvent"]] = relationship("LifecycleEvent", back_populates="bridge", lazy="selectin", cascade="all, delete-orphan")

    @property
    def bridge_id(self) -> str:
        return str(self.id)

    @property
    def bridge_code(self) -> str:
        return self.bridge_id_str

    @bridge_code.setter
    def bridge_code(self, val: str):
        self.bridge_id_str = val

    @property
    def bridge_name(self) -> str:
        return self.name

    @bridge_name.setter
    def bridge_name(self, val: str):
        self.name = val

    @property
    def year_constructed(self):
        return self.engineering.year_built if self.engineering else None

    @property
    def road_name(self):
        return self.location.road_name if self.location else None

    @property
    def district(self):
        return self.location.district if self.location else None

    @property
    def state(self):
        return self.location.state if self.location else "Gujarat"

    @property
    def latitude(self):
        return self.location.latitude if self.location else 0.0

    @property
    def longitude(self):
        return self.location.longitude if self.location else 0.0

class BridgeLocation(Base):
    __tablename__ = 'bridge_locations'
    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    bridge_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey('bridges.id'), unique=True, nullable=False)
    latitude: Mapped[float] = mapped_column(Float, nullable=False)
    longitude: Mapped[float] = mapped_column(Float, nullable=False)
    district: Mapped[str] = mapped_column(String, nullable=False)
    state: Mapped[str] = mapped_column(String, nullable=False, default="Gujarat")
    river_crossing: Mapped[str] = mapped_column(String, nullable=True)
    road_name: Mapped[str] = mapped_column(String, nullable=True)
    taluka: Mapped[str] = mapped_column(String, nullable=True)
    chainage_start: Mapped[float] = mapped_column(Float, nullable=True)
    chainage_end: Mapped[float] = mapped_column(Float, nullable=True)

    bridge: Mapped["Bridge"] = relationship("Bridge", back_populates="location")

class BridgeEngineering(Base):
    __tablename__ = 'bridge_engineering'
    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    bridge_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey('bridges.id'), unique=True, nullable=False)
    total_length: Mapped[float] = mapped_column(Float, nullable=True)
    number_of_spans: Mapped[int] = mapped_column(Integer, nullable=True)
    deck_width: Mapped[float] = mapped_column(Float, nullable=True)
    design_life: Mapped[int] = mapped_column(Integer, nullable=True, default=100)
    year_built: Mapped[int] = mapped_column(Integer, nullable=True)
    superstructure_type: Mapped[str] = mapped_column(String, nullable=True)
    substructure_type: Mapped[str] = mapped_column(String, nullable=True)
    foundation_type: Mapped[str] = mapped_column(String, nullable=True)
    deck_material: Mapped[str] = mapped_column(String, nullable=True)
    number_of_lanes: Mapped[int] = mapped_column(Integer, nullable=True, default=2)
    overall_width: Mapped[float] = mapped_column(Float, nullable=True)
    # Multi-asset extensions
    tunnel_type: Mapped[str] = mapped_column(String, nullable=True) # DRILL_AND_BLAST, TBM, CUT_AND_COVER
    bore_diameter: Mapped[float] = mapped_column(Float, nullable=True)
    ventilation_system: Mapped[str] = mapped_column(String, nullable=True) # JET_FAN, LONGITUDINAL, NATURAL
    pavement_type: Mapped[str] = mapped_column(String, nullable=True) # ASPHALT_FLEXIBLE, CONCRETE_RIGID
    carriageway_width: Mapped[float] = mapped_column(Float, nullable=True)
    culvert_type: Mapped[str] = mapped_column(String, nullable=True) # RCC_BOX, PIPE_CULVERT, SLAB_CULVERT
    opening_span: Mapped[float] = mapped_column(Float, nullable=True)
    clear_height: Mapped[float] = mapped_column(Float, nullable=True)
    
    bridge: Mapped["Bridge"] = relationship("Bridge", back_populates="engineering")
