from typing import Dict, Any, Optional
from datetime import datetime
import asyncio
from core.monitoring import CoreLogger, CoreMetrics
from core.messaging import Message, MessageBroker
from core.schemas import AgentSchema, AgentStatus, AgentType
from .memory import Memory
from .context import Context
from .errors import AgentError
from abc import ABC, abstractmethod
from redis import Redis

class BaseAgent(ABC):
    """Base class for all agents in the system."""
    
    def __init__(
        self,
        agent_id: str,
        name: str,
        agent_type: AgentType,
        redis_client: Optional[Redis] = None,
        redis_url: Optional[str] = None
    ):
        """Initialize the base agent."""
        self.agent_id = agent_id
        self.name = name
        self.agent_type = agent_type
        
        # Initialize memory with either redis_client or redis_url
        if redis_client:
            self.memory = Memory(redis_client=redis_client)
        elif redis_url:
            self.memory = Memory(redis_url=redis_url)
        else:
            raise ValueError("Either redis_client or redis_url must be provided")
        
        self.status = AgentStatus.INITIALIZING
        self.message_broker = None
        self.logger = CoreLogger()
        self.metrics = CoreMetrics()
        self._stop_event = asyncio.Event()
        self._initialized = False
        
        self.state: Dict[str, Any] = {}
        self.context = Context()
        
    async def initialize(self) -> None:
        """Initialize agent resources."""
        if self._initialized:
            return
            
        self.message_broker = MessageBroker()
        await self.memory.initialize()
        await self.context.initialize()
        await self.message_broker.initialize()
        
        self.status = AgentStatus.IDLE
        self._initialized = True
        
    async def cleanup(self) -> None:
        """Cleanup agent resources."""
        if self.message_broker:
            await self.message_broker.cleanup()
        await self.memory.cleanup()
        await self.context.cleanup()
        self._initialized = False
        
    async def process_message(self, message: Message) -> Any:
        """Process incoming messages."""
        try:
            self.logger.logger.info(
                f"Processing message",
                extra={
                    "agent_id": self.agent_id,
                    "message_id": message.id,
                    "message_type": message.type
                }
            )
            
            self.metrics.message_count.inc()
            return await self._handle_message_type(message)
            
        except Exception as e:
            await self.handle_error(e)
            raise
            
    @abstractmethod
    async def _handle_message_type(self, message: Message) -> Any:
        """Internal message handling logic."""
        raise NotImplementedError("Subclasses must implement _handle_message_type")
        
    async def handle_error(self, error: Exception) -> None:
        """Handle agent errors."""
        self.logger.logger.error(
            f"Error in agent {self.name}",
            extra={
                "agent_id": self.agent_id,
                "error": str(error),
                "error_type": type(error).__name__
            }
        )
        self.metrics.error_count.inc()
        
    async def save_to_memory(self, key: str, value: Any) -> None:
        """Save data to agent memory."""
        await self.memory.store(key, value)
        
    async def recall_from_memory(self, key: str) -> Any:
        """Recall data from agent memory."""
        return await self.memory.retrieve(key)
        
    def update_state(self, new_state: Dict[str, Any]) -> None:
        """Update agent state."""
        self.state.update(new_state)