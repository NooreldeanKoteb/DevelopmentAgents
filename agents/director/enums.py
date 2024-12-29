from enum import Enum, auto

class BusinessImpact(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"
    UNKNOWN = "unknown"

class ActionType(str, Enum):
    TASK_CREATION = "task_creation"
    TASK_UPDATE = "task_update"
    RESOURCE_ALLOCATION = "resource_allocation"
    ERROR_HANDLING = "error_handling"
    PROJECT_UPDATE = "project_update"

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