from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel

class TaskData(BaseModel):
    id: str
    name: str
    description: str
    status: str
    assigned_agent: Optional[str]
    dependencies: List[str]
    created_at: datetime
    updated_at: datetime
    estimated_duration: float
    priority: str
    business_impact: str = "low"
    resource_status: dict = {}

class ResourceData(BaseModel):
    id: str
    name: str
    type: str
    capabilities: List[str]
    current_load: float = 0.0
    capacity: float = 1.0
    status: str = "active"
    performance_score: float = 0.5
    last_updated: datetime 