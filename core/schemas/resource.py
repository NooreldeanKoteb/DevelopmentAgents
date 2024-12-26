from pydantic import BaseModel, Field, validator, ConfigDict, field_serializer, field_validator
from datetime import datetime
from typing import Dict, Optional, List, Any
from .enums import ResourceType, ResourceStatus

class ResourceSchema(BaseModel):
    model_config = ConfigDict()

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

    @field_serializer('*', when_used='json')
    def serialize_datetime(self, value: Any, _info) -> Any:
        if isinstance(value, datetime):
            return value.isoformat()
        return value
    
    @field_validator('current_usage')
    @classmethod
    def validate_usage(cls, value: float, info: Any) -> float:
        if value < 0:
            raise ValueError("Usage cannot be negative")
        
        # Get capacity value from the data
        capacity = info.data.get('capacity', 1.0)
        if value > capacity:
            raise ValueError(f"Current usage ({value}) cannot exceed capacity ({capacity})")
        
        return value

    # Add model validation to ensure usage <= capacity
    @field_validator('capacity')
    @classmethod
    def validate_capacity(cls, value: float, info: Any) -> float:
        if value < 0:
            raise ValueError("Capacity cannot be negative")
        
        # Check if current_usage exists and validate against it
        current_usage = info.data.get('current_usage', 0.0)
        if current_usage > value:
            raise ValueError(f"Capacity ({value}) cannot be less than current usage ({current_usage})")
        
        return value