from pydantic import BaseModel
from typing import Optional
from uuid import UUID
from datetime import datetime

class DistressIssueCreate(BaseModel):
    bridge_id: UUID
    title: Optional[str] = "Structural Distress"
    issue_type: Optional[str] = None
    description: Optional[str] = None
    location_details: Optional[str] = None
    source: Optional[str] = "FIELD_INSPECTION"
    severity: Optional[str] = "HIGH"
    photo_url: Optional[str] = None
    reported_by_name: Optional[str] = None

class DistressIssueAssign(BaseModel):
    assigned_inspector_id: Optional[UUID] = None
    assigned_engineer_id: Optional[UUID] = None
    target_date: Optional[datetime] = None
    target_completion_date: Optional[str] = None
    remarks: Optional[str] = None
    notes: Optional[str] = None

class DistressIssueResolve(BaseModel):
    status: str = "RESOLVED"
    remarks: Optional[str] = None

class DistressIssueResponse(BaseModel):
    id: UUID
    bridge_id: UUID
    title: str
    description: Optional[str] = None
    source: str
    severity: str
    photo_url: Optional[str] = None
    status: str
    reported_by_name: Optional[str] = None
    created_at: datetime
    assigned_inspector_id: Optional[UUID] = None
    assigned_engineer_id: Optional[UUID] = None
    target_date: Optional[datetime] = None
    assigned_inspector_name: Optional[str] = None
    assigned_engineer_name: Optional[str] = None
    bridge_code: Optional[str] = None
    bridge_name: Optional[str] = None
