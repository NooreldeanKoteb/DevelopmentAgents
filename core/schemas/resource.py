from typing import List, Optional, Dict, Any
from enum import Enum
from .base import TimestampedSchema, MetadataSchema
from pydantic import Field

class ResourceType(str, Enum):
    CPU = "cpu"
    MEMORY = "memory"
    STORAGE = "storage"
    API = "api"
    MODEL = "model"

class ResourceStatus(str, Enum):
    AVAILABLE = "available"
    IN_USE = "in_use"
    DEPLETED = "depleted"
    ERROR = "error"

class ResourceSchema(TimestampedSchema, MetadataSchema):
    """Schema for resource data."""
    id: str
    name: str
    type: ResourceType
    status: ResourceStatus = ResourceStatus.AVAILABLE
    capacity: float = 1.0
    current_usage: float = 0.0
    limits: Dict[str, float] = Field(default_factory=dict)
    allocated_to: Optional[str] = None 