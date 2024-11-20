"""Resource-related schemas and enums."""
from enum import Enum
from typing import List, Optional
from pydantic import Field
from .base import BaseSchema

class ResourceType(str, Enum):
    """Resource type enumeration."""
    AGENT = "agent"
    COMPUTE = "compute"
    STORAGE = "storage"
    NETWORK = "network"
    DATABASE = "database"
    API = "api"
    MODEL = "model"
    CUSTOM = "custom"

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
    type: ResourceType
    status: ResourceStatus = ResourceStatus.AVAILABLE
    capabilities: List[str] = Field(default_factory=list)
    current_load: float = 0.0
    capacity: float = 1.0
    metadata: dict = Field(default_factory=dict)
    allocated_to: Optional[str] = None 