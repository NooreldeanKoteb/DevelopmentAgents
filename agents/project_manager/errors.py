from agents.base.errors import AgentError
from typing import List, Dict, Any, Optional

class ProjectManagerError(AgentError):
    """Base exception for project manager related errors."""
    pass

class ProjectError(ProjectManagerError):
    """Base exception for project-related errors."""
    pass

class TaskError(ProjectError):
    """Exception for task-related errors."""
    pass

class ResourceError(ProjectError):
    """Exception for resource-related errors."""
    pass

class PlanningError(ProjectError):
    """Exception for planning-related errors."""
    pass

class TaskManagementError(TaskError):
    """Exception for task management operations."""
    pass

class ResourceManagementError(ResourceError):
    """Exception for resource management operations."""
    pass

class ProjectStateError(ProjectError):
    """Exception for invalid project state transitions."""
    def __init__(self, current_state: str, attempted_transition: str):
        self.current_state = current_state
        self.attempted_transition = attempted_transition
        super().__init__(f"Invalid state transition from {current_state} to {attempted_transition}")

class DependencyError(TaskError):
    """Exception for task dependency issues."""
    def __init__(self, task_id: str, dependency_id: str, message: str):
        self.task_id = task_id
        self.dependency_id = dependency_id
        super().__init__(f"Task {task_id} dependency error with {dependency_id}: {message}")

class ResourceAllocationError(ResourceError):
    """Exception for resource allocation issues."""
    def __init__(self, task_id: str, required: Dict[str, Any], available: Dict[str, Any]):
        self.task_id = task_id
        self.required_resources = required
        self.available_resources = available
        super().__init__(f"Failed to allocate resources for task {task_id}")

class ProjectValidationError(ProjectError):
    """Exception for project validation failures."""
    def __init__(self, project_id: str, errors: List[str]):
        self.project_id = project_id
        self.validation_errors = errors
        super().__init__(f"Project {project_id} validation failed: {', '.join(errors)}")

class TaskSchedulingError(TaskError):
    """Exception for task scheduling issues."""
    def __init__(self, task_id: str, reason: str):
        self.task_id = task_id
        super().__init__(f"Failed to schedule task {task_id}: {reason}")

class AgentAssignmentError(TaskError):
    """Exception for agent assignment issues."""
    def __init__(self, task_id: str, agent_id: str, reason: str):
        self.task_id = task_id
        self.agent_id = agent_id
        super().__init__(f"Failed to assign agent {agent_id} to task {task_id}: {reason}")

class ProjectTimelineError(ProjectError):
    """Exception for project timeline issues."""
    def __init__(self, project_id: str, reason: str):
        self.project_id = project_id
        super().__init__(f"Project {project_id} timeline error: {reason}")

class ResourceConflictError(ResourceError):
    """Exception for resource conflicts."""
    def __init__(self, resource_id: str, conflicting_tasks: List[str]):
        self.resource_id = resource_id
        self.conflicting_tasks = conflicting_tasks
        super().__init__(f"Resource conflict for {resource_id}")

class ProjectNotFoundError(ProjectError):
    """Exception for when a project cannot be found."""
    def __init__(self, project_id: str):
        self.project_id = project_id
        super().__init__(f"Project '{project_id}' not found")

class TaskNotFoundError(TaskError):
    """Exception for when a task cannot be found."""
    def __init__(self, task_id: str, project_id: str):
        self.task_id = task_id
        self.project_id = project_id
        super().__init__(f"Task '{task_id}' not found in project '{project_id}'")

class ResourceNotFoundError(ResourceError):
    """Exception for when a resource cannot be found."""
    def __init__(self, resource_id: str, project_id: Optional[str] = None):
        self.resource_id = resource_id
        self.project_id = project_id
        message = f"Resource '{resource_id}' not found"
        if project_id:
            message += f" in project '{project_id}'"
        super().__init__(message) 