from typing import List, Optional, Dict, Any
from enum import Enum
from datetime import datetime
from .base import TimestampedSchema, MetadataSchema

class TaskStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"

class TaskPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class TaskSchema(TimestampedSchema, MetadataSchema):
    """Schema for task data."""
    id: str
    name: str
    description: Optional[str] = None
    status: TaskStatus = TaskStatus.PENDING
    priority: TaskPriority = TaskPriority.MEDIUM
    assigned_agent: Optional[str] = None
    dependencies: List[str] = []
    estimated_duration: float = 0.0
    actual_duration: Optional[float] = None
    progress: float = 0.0
    result: Optional[Dict[str, Any]] = None 