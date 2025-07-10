from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, ConfigDict, field_serializer
import json
from agents.base.enums import TaskType, AgentType
from .enums import BusinessImpact, ProjectStatus
from core.schemas.base import BaseSchema, DescriptiveSchema, MetadataSchema, TimestampedSchema
from core.schemas.resource import ResourceSchema
from core.schemas.enums import Status, Priority

class BaseDirectorSchema(BaseModel):
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

    @field_serializer('*', when_used='json')
    def serialize_datetime(self, value: Any, _info) -> Any:
        if isinstance(value, datetime):
            return value.isoformat()
        return value
    
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

# todo: Figure out the messaging schema first then build this on top
class AgentTaskRequestSchema(BaseDirectorSchema, MetadataSchema, TimestampedSchema):
    agent_type: AgentType  # e.g., "code_generator", "reviewer"
    task_type: TaskType # e.g., "code_generation", "review"
    priority: Priority
    assigned_to: Optional[str] = Field(default=None, description="ID of assigned resource")
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

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary with proper datetime handling."""
        return self.model_dump()

    def to_json(self) -> str:
        """Convert to JSON string."""
        return self.model_dump_json()

class TaskSchema(BaseDirectorSchema, DescriptiveSchema, MetadataSchema, TimestampedSchema):
    """Schema for task data."""
    phase: Optional[str] = Field(default=None, description="Current phase of the task")
    requirements: Dict = Field(default_factory=dict, description="Task requirements")
    implementation_steps: List[str] = Field(default=None, description="Implementation steps")
    expected_outputs: List[str] = Field(default_factory=list, description="Expected outputs")
    completion_criteria: List[str] = Field(default_factory=list, description="Completion criteria")
    business_impact: Optional[BusinessImpact] = Field(default=None, description="Business impact of the task")

    research_required: bool = Field(default=False, description="Whether research is required for the task")
    agent_request: AgentTaskRequestSchema = Field(..., description="AI request for the task")
    status: Status = Field(default=Status.PENDING, description="Current status of the task")
    priority: Priority = Field(..., description="Priority level of the task")
    # required_specializations: List[str] = Field(default_factory=list, description="Required specializations for the task")

    parent_task: Optional[str] = Field(default=None, description="Parent task ID")
    sub_tasks: List["TaskSchema"] = Field(default_factory=list, description="Sub tasks required to complete this task")
    preceding_tasks: List[str] = Field(default_factory=list, description="What is required before starting this task")
    
    estimated_tokens: Optional[int] = Field(default=None, description="Estimated tokens for the task") # for LLM quota management (dont know if this is needed)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary with proper datetime handling."""
        return self.model_dump()

    def to_json(self) -> str:
        """Convert to JSON string."""
        return self.model_dump_json()
    
class ProjectPhase(BaseDirectorSchema, DescriptiveSchema):
    """Project phase schema."""
    order: int = Field(default=0, description="Order of the phase")
    status: ProjectStatus = Field(default=ProjectStatus.PLANNING, description="Status of the phase")
    priority: Priority = Field(default=Priority.UKNOWN, description="Priority of the phase")
    tasks: List[TaskSchema] = Field(default_factory=list, description="Tasks in the phase")
    preceding_phases: List["ProjectPhase"] = Field(default_factory=list, description="Phases that must be completed before this phase")
    resources: List[ResourceSchema] = Field(default_factory=list, description="Resources allocated to the phase")

class ProjectSchema(BaseDirectorSchema, DescriptiveSchema, MetadataSchema, TimestampedSchema):
    """Project schema definition."""
    status: ProjectStatus = ProjectStatus.PLANNING
    phases: List[ProjectPhase] = Field(default_factory=list)
    

    # # for refrence
    # json_schema_extra = {
    #         "example": {
    #             "project_id": "proj_123",
    #             "requesting_agent": "Director",
    #             "target_agents": ["coding_agent", "testing_agent"],
    #             "tasks": [
    #                 {
    #                     "task_id": "task_1",
    #                     "task_type": "code_generation",
    #                     "priority": "high",
    #                     "context": {
    #                         "file_path": "src/feature/new_module.py",
    #                         "requirements": ["Implement async handler", "Add error handling"],
    #                         "code_snippets": {"existing_code": "..."}
    #                     },
    #                     "dependencies": [],
    #                     "constraints": {
    #                         "max_complexity": "O(n)",
    #                         "memory_limit": "100MB",
    #                         "security_requirements": ["no_eval", "input_validation"]
    #                     },
    #                     "expected_output": {
    #                         "format": "python_code",
    #                         "files": ["new_module.py", "test_new_module.py"]
    #                     }
    #                 }
    #             ],
    #             "metadata": {
    #                 "project_name": "AI Development System",
    #                 "priority_level": "high",
    #                 "security_level": "standard"
    #             }
    #         }
    #     }