from typing import Dict, Any, Optional
from datetime import datetime
import asyncio
from core.monitoring import CoreLogger, CoreMetrics
from core.messaging import Message, MessageBroker
from core.schemas import AgentSchema, AgentStatus, AgentType
from .memory import Memory
from .context import Context
from .errors import AgentError

class BaseAgent:
    """Base class for all agents in the system."""
    
    def __init__(self, agent_id: str, name: str, agent_type: AgentType):
        self.id = agent_id
        self.agent_id = agent_id
        self.name = name
        self.type = agent_type
        self.status = AgentStatus.INITIALIZING
        self.message_broker: Optional[MessageBroker] = None
        self.logger = CoreLogger()
        self.metrics = CoreMetrics()
        self._stop_event = asyncio.Event()
        
        self.state: Dict[str, Any] = {}
        self.memory = Memory()
        self.context = Context()
        
    async def initialize(self) -> None:
        """Initialize agent resources."""
        self.message_broker = MessageBroker()
        self.status = AgentStatus.IDLE
        
    async def process_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Process incoming messages."""
        try:
            return await self._handle_message(message)
        except Exception as e:
            await self.handle_error(e)
            raise
            
    async def _handle_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Internal message handling logic."""
        raise NotImplementedError("Subclasses must implement _handle_message")
        
    def update_state(self, new_state: Dict[str, Any]) -> None:
        """Update agent state."""
        self.state.update(new_state)
        
    def handle_error(self, error: Exception) -> None:
        """Handle agent errors."""
        raise NotImplementedError("Subclasses must implement handle_error")