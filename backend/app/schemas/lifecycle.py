from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from uuid import UUID

class LifecycleEventCreate(BaseModel):
    event_type: str
    event_date: datetime
    description: Optional[str] = None
