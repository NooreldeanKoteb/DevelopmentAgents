"""Resource-related schemas and enums."""
from enum import Enum
from typing import List, Optional
from pydantic import Field
from .base import BaseSchema
from .enums import ResourceType, ResourceStatus

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

__all__ = ['ResourceSchema', 'ResourceType', 'ResourceStatus'] 