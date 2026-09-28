from pydantic import BaseModel
from typing import Optional
from uuid import UUID

class MaintenanceCreate(BaseModel):
    maintenance_type: str
    priority: str
    description: Optional[str] = None
    estimated_cost: Optional[float] = None

class MaintenanceStatusUpdate(BaseModel):
    action: str # estimate, sanction, award_tender, start, complete, verify
    remarks: Optional[str] = None
    estimated_cost: Optional[float] = None
    sanction_number: Optional[str] = None
    sanctioned_amount: Optional[float] = None
    tender_number: Optional[str] = None
    work_order_number: Optional[str] = None
    tender_value: Optional[float] = None
    assigned_contractor: Optional[str] = None
    actual_cost: Optional[float] = None
