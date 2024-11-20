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
        self.name = name
        self.type = agent_type
        self.status = AgentStatus.INITIALIZING
        self.message_broker: Optional[MessageBroker] = None
        self.logger = CoreLogger()
        self.metrics = CoreMetrics()
        self._stop_event = asyncio.Event()
        
    async def initialize(self) -> None:
        """Initialize agent resources."""
        self.message_broker = MessageBroker()
        self.status = AgentStatus.IDLE