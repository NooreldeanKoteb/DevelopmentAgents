from core.config import (
    get_settings,
    setup_logging,
    initialize_monitoring,
    monitor_operation,
    AgentType
)

# Initialize configuration
setup_logging()
initialize_monitoring()

# Use settings
settings = get_settings() 