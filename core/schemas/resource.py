from pydantic import BaseModel, Field, validator
from datetime import datetime
from typing import Dict, Optional, List
from .enums import ResourceType, ResourceStatus

class ResourceSchema(BaseModel):
    id: str = Field(..., description="Unique identifier")
    name: str = Field(..., description="Resource name")
    type: ResourceType = Field(..., description="Resource type")
    status: ResourceStatus = Field(default=ResourceStatus.AVAILABLE, description="Current status")
    capacity: float = Field(default=1.0, ge=0.0, description="Resource capacity")
    current_usage: float = Field(default=0.0, ge=0.0, description="Current resource usage")
    limits: Dict[str, float] = Field(default_factory=dict, description="Resource limits")
    allocated_to: Optional[str] = Field(default=None, description="ID of task/agent this resource is allocated to")
    created_at: Optional[datetime] = Field(default_factory=datetime.now, description="Creation timestamp")
    updated_at: Optional[datetime] = Field(default_factory=datetime.now, description="Last update timestamp")
    metadata: Dict = Field(default_factory=dict, description="Additional metadata")

    @validator('current_usage')
    def validate_usage(cls, v, values):
        if 'capacity' in values and v > values['capacity']:
            raise ValueError('Current usage cannot exceed capacity')
        return v

    class Config:
        validate_assignment = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }