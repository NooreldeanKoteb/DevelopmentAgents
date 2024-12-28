from enum import Enum

class ResourceType(str, Enum):
    """Resource type enumeration."""
    CPU = "cpu"
    MEMORY = "memory"
    STORAGE = "storage"
    API = "api"
    MODEL = "model"
    AGENT = "agent"
    COMPUTE = "compute"
    NETWORK = "network"
    DATABASE = "database"
    CUSTOM = "custom"

class ResourceStatus(str, Enum):
    """Resource status enumeration."""
    AVAILABLE = "available"
    IN_USE = "in_use"
    DEPLETED = "depleted"
    MAINTENANCE = "maintenance"
    ERROR = "error"
    UNAVAILABLE = "unavailable"

class TaskStatus(str, Enum):
    """Task status enumeration."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    BLOCKED = "blocked"
    CANCELLED = "cancelled"

class TaskPriority(str, Enum):
    """Task priority enumeration."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"
    UKNOWN = "unknown"

class BusinessImpact(str, Enum):
    """Business impact enumeration."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class AgentType(Enum):
    """Types of agents in the system."""
    PROJECT_MANAGER = "project_manager"
    KNOWLEDGE = "knowledge"
    CODING = "coding"
    TESTING = "testing"
    SECURITY = "security"
    DOCUMENTATION = "documentation" 