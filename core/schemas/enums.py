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