"""Agent-related schemas and enums."""
from enum import Enum
from typing import List, Optional, Dict
from .base import BaseSchema

class AgentStatus(str, Enum):
    """Agent status enumeration."""
    IDLE = "idle"
    BUSY = "busy"
    OFFLINE = "offline"
    ERROR = "error"
    INITIALIZING = "initializing"

class AgentType(str, Enum):
    """Agent type enumeration."""
    PROJECT_MANAGER = "project_manager"
    KNOWLEDGE = "knowledge"
    CODING = "coding"
    TESTING = "testing"
    SECURITY = "security"
    DOCUMENTATION = "documentation"

class AgentSchema(BaseSchema):
    """Agent schema definition."""
    name: str
    type: AgentType
    status: AgentStatus = AgentStatus.INITIALIZING
    capabilities: List[str] = []
    current_task: Optional[str] = None
    performance_metrics: Dict[str, float] = {} 