from enum import Enum

class Environment(str, Enum):
    """Environment types."""
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"

class LogLevel(str, Enum):
    """Logging levels."""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"

class AgentType(str, Enum):
    """Types of agents in the system."""
    PROJECT_MANAGER = "project_manager"
    KNOWLEDGE = "knowledge"
    CODING = "coding"
    TESTING = "testing"
    ENVIRONMENT = "environment"
    SECURITY = "security"
    DOCUMENTATION = "documentation" 