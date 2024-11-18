from enum import Enum

class ActionType(Enum):
    PROJECT_UPDATE = "project_update"
    RESOURCE_ALLOCATION = "resource_allocation"
    TASK_CREATION = "task_creation"
    TASK_UPDATE = "task_update"
    PRIORITY_ADJUSTMENT = "priority_adjustment"
    TIMELINE_UPDATE = "timeline_update"
    ERROR_HANDLING = "error_handling"
    DEPENDENCY_UPDATE = "dependency_update"
    STATUS_CHANGE = "status_change"

class Priority(Enum):
    CRITICAL = "critical"  # Score >= 80
    HIGH = "high"         # Score >= 60
    MEDIUM = "medium"     # Score >= 40
    LOW = "low"          # Score < 40 