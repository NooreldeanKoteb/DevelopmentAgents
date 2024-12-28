from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, ConfigDict
from core.schemas.enums import TaskStatus, TaskPriority
import json
from agents.base.enums import TaskType, AgentName

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


class ProjectRequest(BaseModel):
    project_id: str
    request_id: str = Field(default_factory=lambda: str(uuid4()))
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    requesting_agent: str
    target_agents: List[str] = Field(
        description="List of agent IDs that should handle the tasks"
    )
    tasks: List[AITaskRequest]
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional project-level metadata"
    )
    deadline: Optional[datetime] = None
    max_retries: int = Field(default=3, ge=0)
    required_capabilities: List[str] = Field(
        default_factory=list,
        description="Required capabilities for handling the tasks"
    )
    
    class Config:
        use_enum_values = True
        json_schema_extra = {
            "example": {
                "project_id": "proj_123",
                "requesting_agent": "Director",
                "target_agents": ["coding_agent", "testing_agent"],
                "tasks": [
                    {
                        "task_id": "task_1",
                        "task_type": "code_generation",
                        "priority": "high",
                        "context": {
                            "file_path": "src/feature/new_module.py",
                            "requirements": ["Implement async handler", "Add error handling"],
                            "code_snippets": {"existing_code": "..."}
                        },
                        "dependencies": [],
                        "constraints": {
                            "max_complexity": "O(n)",
                            "memory_limit": "100MB",
                            "security_requirements": ["no_eval", "input_validation"]
                        },
                        "expected_output": {
                            "format": "python_code",
                            "files": ["new_module.py", "test_new_module.py"]
                        }
                    }
                ],
                "metadata": {
                    "project_name": "AI Development System",
                    "priority_level": "high",
                    "security_level": "standard"
                }
            }
        }

class AgentTaskRequest(BaseModel):
    id: str
    agent_type: AgentName  # e.g., "code_generator", "reviewer"
    task_type: TaskType # e.g., "code_generation", "review"
    priority: TaskPriority
    context: Optional[Dict[str, Any]] = {
        "files": Optional[List[str]],
        "code_snippets": Optional[List[str]],
        "steps": Optional[List[str]],
        "requirements": Optional[List[str]]
    }
    dependencies: Optional[List[str]] = Field(
        default_factory=list,
        description="List of task IDs that must be completed before this task"
    )
    constraints: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Specific constraints l ike memory limits, time limits, security requirements"
    ) # Memory limits, time limits, security requirements
    expected_output: Optional[Dict[str, Any]] = Field(
        description="Expected format and structure of the task output"
    ) # Files
    created_at: datetime = Field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = Field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary with proper datetime handling."""
        return self.model_dump()

    def to_json(self) -> str:
        """Convert to JSON string."""
        return self.model_dump_json()

class TaskSchema(BaseProjectModel):
    """Schema for task data."""
    id: str
    title: str
    description: str
    research_required: bool
    ai_request: AgentTaskRequest
    status: TaskStatus = TaskStatus.PENDING
    priority: TaskPriority = Field(default_factory=TaskPriority.UKNOWN)
    required_specializations: List[str] = Field(default_factory=list)  # e.g., ["python", "api_design"]
    sub_tasks: List["TaskSchema"] = Field(default_factory=list) #What is required to complete this task
    preceding_tasks: List[str] = Field(default_factory=list) #What is required before starting this task
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)

    estimated_tokens: Optional[int] = None  # for LLM quota management (dont know if this is needed)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary with proper datetime handling."""
        return self.model_dump()

    def to_json(self) -> str:
        """Convert to JSON string."""
        return self.model_dump_json()
