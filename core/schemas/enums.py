from enum import Enum

class ResourceType(str, Enum):
    """Resource type enumeration."""
    AGENT = "agent"

    #not sure if we need these
    COMPUTE = "compute"
    NETWORK = "network"
    DATABASE = "database"
    CPU = "cpu"
    MEMORY = "memory"
    STORAGE = "storage"
    API = "api"
    MODEL = "model"
    CUSTOM = "custom"

class ResourceStatus(str, Enum):
    """Resource status enumeration."""
    AVAILABLE = "available"
    IN_USE = "in_use"
    DEPLETED = "depleted"
    MAINTENANCE = "maintenance"
    ERROR = "error"
    UNAVAILABLE = "unavailable"

class Status(str, Enum):
    """Status enumeration."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    PRIORITY_ADJUSTMENT = "priority_adjustment"

class Priority(str, Enum):
    """Priority enumeration."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"
    UKNOWN = "unknown"

class MessageStatus(str, Enum):
    """Message status enumeration."""
    PENDING = "pending"
    DELIVERED = "delivered"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    RETRYING = "retrying"

class MessageType(str, Enum):
    """Message type enumeration."""
    TASK_CREATION = "task_creation"
    TASK_UPDATE = "task_update"
    TASK_COMPLETION = "task_completion"
    TASK_FAILURE = "task_failure"
    RESOURCE_ALLOCATION = "resource_allocation"
    RESOURCE_UPDATE = "resource_update"
    PROJECT_UPDATE = "project_update"
    STATUS_UPDATE = "status_update"
    ERROR = "error"
    INFO = "info"
    WARNING = "warning"
    QUERY = "query"
    RESPONSE = "response"
    COMMAND = "command"