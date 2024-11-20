from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, ConfigDict
from core.schemas.enums import TaskStatus, TaskPriority, BusinessImpact

class BaseProjectModel(BaseModel):
    """Base model with common configuration."""
    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        validate_assignment=True,
        extra='forbid',
        populate_by_name=True
    )

class TaskData(BaseProjectModel):
    id: str
    name: str
    description: Optional[str] = None
    status: TaskStatus = TaskStatus.PENDING
    priority: TaskPriority = TaskPriority.MEDIUM
    business_impact: BusinessImpact = BusinessImpact.LOW
    estimated_duration: float = 1.0
    assigned_agent: Optional[str] = None
    dependencies: List[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

class ResourceData(BaseProjectModel):
    id: str
    name: str
    type: str
    status: str
    capabilities: List[str] = Field(default_factory=list)
    current_load: float = 0.0
    capacity: float = 1.0
    performance_score: float = 0.0

class ProjectResponse(BaseProjectModel):
    action_type: str
    tasks: List[Dict[str, Any]] = Field(default_factory=list)
    timeline: Dict[str, Any] = Field(default_factory=dict)
    resources: List[Dict[str, Any]] = Field(default_factory=list)

class TaskSchema(BaseProjectModel):
    """Schema for task data."""
    id: str
    title: str
    description: str
    status: TaskStatus = TaskStatus.PENDING
    priority: TaskPriority = TaskPriority.MEDIUM
    assignee: Optional[str] = None
    dependencies: List[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = Field(default_factory=dict) 