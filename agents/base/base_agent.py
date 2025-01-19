from typing import Dict, Any, Optional, List
from datetime import datetime
import asyncio
from core.monitoring import CoreLogger, CoreMetrics
from core.messaging import Message, MessageBroker
from .memory import Memory
from .schemas import AgentSchema
from .errors import AgentError
from abc import ABC, abstractmethod
from redis import Redis
from agents.base.enums import AgentStatus, AgentType
from .schemas import AgentState, AgentMode

class BaseAgent(ABC):
    """Base class for all agents in the system."""
    
    def __init__(
        self,
        name: str,
        agent_type: AgentType,
        capabilities: Optional[List[str]] = None,
        redis_client: Optional[Redis] = None,
        redis_url: Optional[str] = None
    ):
        """Initialize the base agent."""

        # Initialize schema
        self.agent = AgentSchema(
            type=agent_type,
            name=name,
            capabilities=capabilities,
            agent_state=AgentState(
                status=AgentStatus.INITIALIZING,
                mode=AgentMode.DEVELOPMENT,
                )
        )
        
        # Initialize memory with either redis_client or redis_url
        if redis_client:
            self.memory = Memory(redis_client=redis_client)
        elif redis_url:
            self.memory = Memory(redis_url=redis_url)
        else:
            raise ValueError("Either redis_client or redis_url must be provided")
        
        self.message_broker = None
        self.logger = CoreLogger()
        self.metrics = CoreMetrics()
        self._stop_event = asyncio.Event()
        self._initialized = False
        
    def get_capabilities(self) -> List[str]:
        """Get agent capabilities. Override in subclasses."""
        return self.agent.capabilities
        
    async def initialize(self) -> None:
        """Initialize agent resources."""
        if self._initialized:
            return
            
        self.message_broker = MessageBroker()
        await self.memory.initialize()
        await self.message_broker.initialize()
        
        await self.agent.update_state(status=AgentStatus.IDLE)
        self._initialized = True
        
    async def cleanup(self) -> None:
        """Cleanup agent resources."""
        if self.message_broker:
            await self.message_broker.cleanup()
        await self.memory.cleanup()
        await self.agent.cleanup()
        self._initialized = False
        
    async def process_message(self, message: Message) -> Any:
        """Process incoming messages."""
        try:
            message_type = getattr(message, 'type', None) or getattr(message, 'topic', 'unknown')
            
            self.logger.logger.info(
                f"Processing message",
                extra={
                    "agent_id": self.agent.id,
                    "message_id": message.id,
                    "message_type": message_type
                }
            )
            
            # Include all required labels when incrementing metrics
            self.metrics.message_count.labels(
                agent_id=self.agent.id,
                agent_type=self.agent.type,
                type=message_type
            ).inc()
            
            # Update schema with message
            await self.agent.add_to_history(message)
            self.agent.last_message = message
            
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
                "agent_id": self.agentid,
                "error": str(error),
                "error_type": type(error).__name__
            }
        )
        self.metrics.error_count.labels(
            agent_id=self.agent.id,
            agent_type=self.agent.type
        ).inc()
        
        # Update error count in schema
        await self.agent.update_state(error_count=self.schema.agent_state.error_count + 1)
        
    async def save_to_memory(self, key: str, value: Any) -> None:
        """Save data to agent memory."""
        try:
            # Convert Pydantic models to dict if present
            if hasattr(value, 'model_dump'):
                value = value.model_dump()
            elif hasattr(value, 'dict'):
                value = value.dict()
            
            await self.memory.store(key, value)
        except Exception as e:
            raise AgentError(f"Failed to save to memory: {str(e)}")
        
    async def recall_from_memory(self, key: str) -> Any:
        """Recall data from agent memory."""
        return await self.memory.retrieve(key)
    
    async def get_agent_state(self) -> AgentState:
        """Get the current state of the agent."""
        return self.agent.agent_state
