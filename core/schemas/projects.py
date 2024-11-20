from enum import Enum
from typing import List, Dict, Any, Optional
from datetime import datetime
from pydantic import Field

from .base import BaseSchema
from .tasks import TaskSchema
from .resources import ResourceSchema

class ProjectStatus(str, Enum):
    """Project status enumeration."""
    PLANNING = "planning"
    IN_PROGRESS = "in_progress"
    ON_HOLD = "on_hold"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    FAILED = "failed"
    REVIEWING = "reviewing"
    ARCHIVED = "archived"

class ProjectPhase(BaseSchema):
    """Project phase schema."""
    name: str
    description: Optional[str] = None
    order: int
    tasks: List[TaskSchema] = Field(default_factory=list)
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    status: ProjectStatus = ProjectStatus.PLANNING
    dependencies: List[str] = Field(default_factory=list)

class ProjectSchema(BaseSchema):
    """Project schema definition."""
    name: str
    description: Optional[str] = None
    status: ProjectStatus = ProjectStatus.PLANNING
    phases: List[ProjectPhase] = Field(default_factory=list)
    tasks: List[TaskSchema] = Field(default_factory=list)
    resources: List[ResourceSchema] = Field(default_factory=list)
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None 