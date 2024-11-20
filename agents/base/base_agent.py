from typing import Dict, Any, Optional, List
import asyncio
from datetime import datetime
from uuid import uuid4

from core.messaging import Message, MessageBroker
from core.schemas import AgentSchema, AgentStatus, AgentType
from core.monitoring import CoreLogger, CoreMetrics
from .memory import AgentMemory
from .context import AgentContext
from .errors import AgentError

class BaseAgent:
    """Base class for all agents in the system."""
    
    def __init__(
        self,
        agent_id: Optional[str] = None,
        name: str = "BaseAgent",
        agent_type: AgentType = AgentType.PROJECT_MANAGER,
        capabilities: List[str] = None
    ):
        self.id = agent_id or str(uuid4())
        self.name = name
        self.type = agent_type
        self.status = AgentStatus.IDLE
        self.capabilities = capabilities or []
        
        # Core components
        self.message_broker: Optional[MessageBroker] = None
        self.memory: Optional[AgentMemory] = None
        self.context: Optional[AgentContext] = None
        self.logger: Optional[CoreLogger] = None
        self.metrics: Optional[CoreMetrics] = None
        
        # State
        self.current_task: Optional[str] = None
        self.performance_metrics: Dict[str, float] = {}
        self._stop_event: asyncio.Event = asyncio.Event()
        
    async def initialize(self) -> None:
        """Initialize agent components."""
        try:
            self.message_broker = MessageBroker()
            self.memory = AgentMemory(agent_id=self.id)
            self.context = AgentContext()
            self.logger = CoreLogger()
            self.metrics = CoreMetrics()
            
            # Subscribe to relevant topics
            await self.message_broker.subscribe(
                f"agent.{self.id}",
                self._handle_message
            )
            await self.message_broker.subscribe(
                "broadcast",
                self._handle_message
            )
            
            self.logger.logger.info(
                f"Agent {self.id} initialized",
                extra={"agent_type": self.type.value}
            )
            
        except Exception as e:
            raise AgentError(f"Agent initialization failed: {str(e)}")
            
    async def start(self) -> None:
        """Start agent processing loop."""
        self.status = AgentStatus.IDLE
        self._stop_event.clear()
        
        try:
            while not self._stop_event.is_set():
                try:
                    message = await self.message_broker.get_message(f"agent.{self.id}")
                    if message:
                        await self._process_message(message)
                except Exception as e:
                    self.logger.logger.error(
                        f"Message processing error: {str(e)}",
                        extra={"agent_id": self.id}
                    )
                await asyncio.sleep(0.1)
                
        except Exception as e:
            self.status = AgentStatus.ERROR
            raise AgentError(f"Agent processing loop failed: {str(e)}")
            
    async def stop(self) -> None:
        """Stop agent processing."""
        self._stop_event.set()
        self.status = AgentStatus.OFFLINE
        
    async def _process_message(self, message: Message) -> None:
        """Process incoming message."""
        try:
            start_time = datetime.now()
            
            self.status = AgentStatus.BUSY
            self.metrics.message_count.labels(
                agent_type=self.type.value,
                status="received"
            ).inc()
            
            # Update context with message
            self.context.update(message)
            
            # Process message
            response = await self.process_message(message)
            
            if response:
                await self.message_broker.publish(response)
                
            # Update metrics
            processing_time = (datetime.now() - start_time).total_seconds()
            self.metrics.message_processing_time.labels(
                agent_type=self.type.value
            ).observe(processing_time)
            
            self.status = AgentStatus.IDLE
            
        except Exception as e:
            self.metrics.message_count.labels(
                agent_type=self.type.value,
                status="error"
            ).inc()
            raise AgentError(f"Message processing failed: {str(e)}")
            
    async def process_message(self, message: Message) -> Optional[Message]:
        """Process message - to be implemented by specific agents."""
        raise NotImplementedError
        
    async def execute_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute task - to be implemented by specific agents."""
        raise NotImplementedError
        
    def get_state(self) -> AgentSchema:
        """Get current agent state."""
        return AgentSchema(
            id=self.id,
            name=self.name,
            type=self.type,
            status=self.status,
            capabilities=self.capabilities,
            current_task=self.current_task,
            performance_metrics=self.performance_metrics
        )
        
    async def save_to_memory(self, key: str, value: Any) -> None:
        """Save data to agent memory."""
        await self.memory.store(key, value)
        
    async def recall_from_memory(self, key: str) -> Optional[Any]:
        """Recall data from agent memory."""
        return await self.memory.retrieve(key)
        
    async def __aenter__(self):
        """Async context manager entry."""
        await self.initialize()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.stop() 