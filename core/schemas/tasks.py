"""Task-related schemas and enums."""
from enum import Enum
from typing import List, Optional
from datetime import datetime
from pydantic import Field
from .base import BaseSchema

class TaskStatus(str, Enum):
    """Task status enumeration."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    BLOCKED = "blocked"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    PAUSED = "paused"
    REVIEWING = "reviewing"

class TaskPriority(str, Enum):
    """Task priority enumeration."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

class BusinessImpact(str, Enum):
    """Business impact enumeration."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

class TaskSchema(BaseSchema):
    """Task schema definition."""
    name: str
    description: Optional[str] = None
    status: TaskStatus = TaskStatus.PENDING
    priority: TaskPriority = TaskPriority.MEDIUM
    business_impact: BusinessImpact = BusinessImpact.LOW
    estimated_duration: float = 1.0
    assigned_to: Optional[str] = None
    dependencies: List[str] = Field(default_factory=list)
    phase: Optional[str] = None
    progress: float = 0.0 