from agents.base.errors import AgentError

class ProjectManagerError(AgentError):
    """Base exception for project manager errors."""
    pass

class PlanningError(ProjectManagerError):
    """Exception raised for errors in project planning."""
    pass

class TaskManagementError(ProjectManagerError):
    """Exception raised for errors in task management."""
    pass

class ResourceManagementError(ProjectManagerError):
    """Exception raised for errors in resource management."""
    pass

class ProjectStateError(ProjectManagerError):
    """Exception raised for invalid project state transitions."""
    def __init__(self, current_state: str, attempted_transition: str):
        self.current_state = current_state
        self.attempted_transition = attempted_transition
        message = f"Invalid state transition from '{current_state}' to '{attempted_transition}'"
        super().__init__(message)

class DependencyError(ProjectManagerError):
    """Exception raised for dependency-related errors."""
    def __init__(self, task_id: str, dependency_id: str, issue: str):
        self.task_id = task_id
        self.dependency_id = dependency_id
        message = f"Dependency error for task '{task_id}' with dependency '{dependency_id}': {issue}"
        super().__init__(message)

class ResourceAllocationError(ProjectManagerError):
    """Exception raised when resource allocation fails."""
    def __init__(self, task_id: str, required_resources: dict, available_resources: dict):
        self.task_id = task_id
        self.required_resources = required_resources
        self.available_resources = available_resources
        message = (
            f"Failed to allocate resources for task '{task_id}'. "
            f"Required: {required_resources}, Available: {available_resources}"
        )
        super().__init__(message)

class ProjectValidationError(ProjectManagerError):
    """Exception raised for project validation errors."""
    def __init__(self, project_id: str, validation_errors: list):
        self.project_id = project_id
        self.validation_errors = validation_errors
        message = f"Project '{project_id}' validation failed: {validation_errors}"
        super().__init__(message)

class TaskSchedulingError(ProjectManagerError):
    """Exception raised for task scheduling errors."""
    def __init__(self, task_id: str, reason: str):
        self.task_id = task_id
        message = f"Failed to schedule task '{task_id}': {reason}"
        super().__init__(message)

class AgentAssignmentError(ProjectManagerError):
    """Exception raised for agent assignment errors."""
    def __init__(self, task_id: str, agent_id: str, reason: str):
        self.task_id = task_id
        self.agent_id = agent_id
        message = f"Failed to assign agent '{agent_id}' to task '{task_id}': {reason}"
        super().__init__(message)

class ProjectTimelineError(ProjectManagerError):
    """Exception raised for timeline-related errors."""
    def __init__(self, project_id: str, timeline_issue: str):
        self.project_id = project_id
        message = f"Project '{project_id}' timeline error: {timeline_issue}"
        super().__init__(message)

class ResourceConflictError(ProjectManagerError):
    """Exception raised for resource conflicts."""
    def __init__(self, resource_id: str, conflicting_tasks: list):
        self.resource_id = resource_id
        self.conflicting_tasks = conflicting_tasks
        message = (
            f"Resource conflict for '{resource_id}' between tasks: {conflicting_tasks}"
        )
        super().__init__(message)

class ProjectNotFoundError(ProjectManagerError):
    """Exception raised when project is not found."""
    def __init__(self, project_id: str):
        self.project_id = project_id
        message = f"Project '{project_id}' not found"
        super().__init__(message)

class TaskNotFoundError(ProjectManagerError):
    """Exception raised when task is not found."""
    def __init__(self, task_id: str, project_id: str = None):
        self.task_id = task_id
        self.project_id = project_id
        message = f"Task '{task_id}' not found"
        if project_id:
            message += f" in project '{project_id}'"
        super().__init__(message) 