from core.config import (
    get_settings,
    setup_logging,
    initialize_monitoring,
    monitor_operation,
    AgentType
)
from typing import Any
from agents.base.message import Message

# Initialize configuration
setup_logging()
initialize_monitoring()

# Use settings
settings = get_settings() 

class BaseAgent:
    async def handle_error(self, error: Exception) -> None:
        """Handle agent errors."""
        # Implement error handling logic
        raise NotImplementedError

    async def process_message(self, message: Message) -> Any:
        """Process incoming messages."""
        raise NotImplementedError 