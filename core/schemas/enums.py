from enum import Enum

class TaskStatus(Enum):
    """Task status states."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    BLOCKED = "blocked"
    COMPLETED = "completed"
    FAILED = "failed"

class TaskPriority(Enum):
    """Task priority levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class BusinessImpact(Enum):
    """Business impact levels."""
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