from typing import Dict, Any, Optional, List
from enum import Enum
from .base import TimestampedSchema, MetadataSchema
from pydantic import Field

class AgentStatus(str, Enum):
    IDLE = "idle"
    BUSY = "busy"
    ERROR = "error"
    OFFLINE = "offline"

class AgentType(str, Enum):
    PROJECT_MANAGER = "project_manager"
    KNOWLEDGE = "knowledge"
    CODING = "coding"
    TESTING = "testing"
    SECURITY = "security"
    DOCUMENTATION = "documentation"

class AgentSchema(TimestampedSchema, MetadataSchema):
    """Base schema for agent data."""
    id: str
    name: str
    type: AgentType
    status: AgentStatus = AgentStatus.IDLE
    capabilities: List[str] = []
    current_task: Optional[str] = None
    performance_metrics: Dict[str, float] = Field(default_factory=dict) 