from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Optional, Dict
from .enums import TaskStatus, TaskPriority, BusinessImpact

class TaskSchema(BaseModel):
    # Required fields
    id: str = Field(..., description="Unique identifier for the task")
    name: str = Field(..., description="Name of the task")
    description: str = Field(..., description="Description of the task")
    status: TaskStatus = Field(default=TaskStatus.PENDING, description="Current status of the task")
    priority: TaskPriority = Field(..., description="Priority level of the task")
    business_impact: BusinessImpact = Field(..., description="Business impact level of the task")
    estimated_duration: float = Field(..., ge=0, description="Estimated duration in hours")
    
    # Optional fields with defaults
    dependencies: List[str] = Field(default_factory=list, description="List of dependent task IDs")
    created_at: datetime = Field(default_factory=datetime.now, description="Task creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.now, description="Task last update timestamp")
    metadata: Dict = Field(default_factory=dict, description="Additional metadata")
    
    # Planning fields
    phase: Optional[str] = Field(default=None, description="Current phase of the task")
    progress: float = Field(default=0.0, ge=0, le=100, description="Task progress percentage")
    assigned_to: Optional[str] = Field(default=None, description="ID of assigned resource")
    
    # Additional fields
    tags: List[str] = Field(default_factory=list, description="Task tags")
    due_date: Optional[datetime] = Field(default=None, description="Task due date")
    subtasks: List[str] = Field(default_factory=list, description="List of subtask IDs")
    parent_task: Optional[str] = Field(default=None, description="Parent task ID")
    requirements: Dict = Field(default_factory=dict, description="Task requirements")
    completion_criteria: List[str] = Field(default_factory=list, description="Completion criteria")
    notes: str = Field(default="", description="Additional notes")

    class Config:
        validate_assignment = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }