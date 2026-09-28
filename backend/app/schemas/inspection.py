from pydantic import BaseModel
from typing import List, Optional
from uuid import UUID
from datetime import datetime

class ComponentCreate(BaseModel):
    component_type: str
    condition_rating: int
    notes: Optional[str] = None

class DefectCreate(BaseModel):
    severity: str
    description: str
    component_id: Optional[UUID] = None

class InspectionCreate(BaseModel):
    inspection_type: str
    scheduled_date: Optional[datetime] = None
    weather_condition: Optional[str] = "CLEAR"
    overall_comments: Optional[str] = None
    components: List[ComponentCreate] = []
    defects: List[DefectCreate] = []
    
    # Proof of Inspection & GPS Geofencing
    inspector_gps_latitude: Optional[float] = None
    inspector_gps_longitude: Optional[float] = None
    photo_evidence_url: Optional[str] = None

class InspectionCounterSign(BaseModel):
    verification_remarks: Optional[str] = None
