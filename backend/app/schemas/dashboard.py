from pydantic import BaseModel
from typing import Dict

class DashboardSummaryResponse(BaseModel):
    total_bridges: int
    by_status: Dict[str, int]
    by_condition: Dict[str, int]
    critical_count: int
    overdue_inspections: int
