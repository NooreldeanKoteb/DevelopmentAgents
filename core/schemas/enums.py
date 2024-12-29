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