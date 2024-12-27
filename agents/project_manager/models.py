from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, ConfigDict
from core.schemas.enums import TaskStatus, TaskPriority, BusinessImpact
import json

class BaseProjectModel(BaseModel):
    """Base model with common configuration."""
    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        validate_assignment=True,
        extra='forbid',
        populate_by_name=True,
        json_encoders={
            datetime: lambda v: v.isoformat()
        }
    )

    def model_dump(self, *args, **kwargs):
        """Convert to dictionary with datetime handling."""
        exclude_none = kwargs.pop('exclude_none', True)
        by_alias = kwargs.pop('by_alias', True)
        
        dump = super().model_dump(
            exclude_none=exclude_none,
            by_alias=by_alias,
            *args,
            **kwargs
        )
        
        # Convert datetime objects to ISO format strings
        for k, v in dump.items():
            if isinstance(v, datetime):
                dump[k] = v.isoformat()
        return dump

    def model_dump_json(self, *args, **kwargs):
        """Convert to JSON string."""
        kwargs.setdefault('indent', 2)
        return json.dumps(self.model_dump(*args, **kwargs))

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
    resources: Dict[str, Dict[str, Any]] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary with proper datetime handling."""
        return self.model_dump()

    def to_json(self) -> str:
        """Convert to JSON string."""
        return self.model_dump_json()

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