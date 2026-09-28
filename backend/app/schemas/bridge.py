from pydantic import BaseModel
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
    # Multi-asset fields
    tunnel_type: Optional[str] = None
    bore_diameter: Optional[float] = None
    ventilation_system: Optional[str] = None
    pavement_type: Optional[str] = None
    carriageway_width: Optional[float] = None
    culvert_type: Optional[str] = None
    opening_span: Optional[float] = None
    clear_height: Optional[float] = None

class BridgeCreate(BaseModel):
    bridge_id_str: str
    name: str
    asset_type: Optional[str] = "BRIDGE"
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
    asset_type: Optional[str] = "BRIDGE"
    bridge_type: str
    current_status: str
    district: Optional[str] = None
    latest_health_index: Optional[float] = None

class BridgeResponse(BridgeCreate):
    id: UUID
    location: BridgeLocationBase
    engineering: BridgeEngineeringBase
