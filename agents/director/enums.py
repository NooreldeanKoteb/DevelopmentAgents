from enum import Enum, auto

class TaskStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    PRIORITY_ADJUSTMENT = "priority_adjustment"

class Priority(Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

class BusinessImpact(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

class ActionType(str, Enum):
    TASK_CREATION = "task_creation"
    TASK_UPDATE = "task_update"
    RESOURCE_ALLOCATION = "resource_allocation"
    ERROR_HANDLING = "error_handling"
    PROJECT_UPDATE = "project_update"