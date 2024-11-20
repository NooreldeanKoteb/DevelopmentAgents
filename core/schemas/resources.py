"""Resource-related schemas and enums."""
from enum import Enum
from typing import List, Optional
from .base import BaseSchema

class ResourceStatus(str, Enum):
    """Resource status enumeration."""
    AVAILABLE = "available"
    IN_USE = "in_use"
    UNAVAILABLE = "unavailable"
    MAINTENANCE = "maintenance"
    ERROR = "error"

class ResourceSchema(BaseSchema):
    """Resource schema definition."""
    name: str
    type: str
    status: ResourceStatus = ResourceStatus.AVAILABLE
    capabilities: List[str] = []
    allocated_to: Optional[str] = None 