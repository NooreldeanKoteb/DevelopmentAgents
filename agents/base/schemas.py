from agents.base.enums import AgentStatus, AgentMode
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from core.schemas.base import TimestampedSchema, MetadataSchema, BaseSchema
from agents.base.enums import AgentType
from core.messaging import Message
class AgentState(BaseModel):
    """Current state of the agent."""
    status: AgentStatus = Field(default=AgentStatus.IDLE, description="Current status of the agent")
    mode: AgentMode = Field(default=None, description="Current mode of the agent")
    current_task_id: Optional[str] = Field(default=None, description="ID of the current task")
    current_operation: Optional[str] = Field(default=None, description="Current operation being performed")
    last_active: datetime = Field(default_factory=datetime.now, description="Last time the agent was active")
    error_count: int = Field(default=0, description="Number of errors encountered by the agent")
    success_count: int = Field(default=0, description="Number of successful operations performed by the agent")
    # active_tasks: List[str] = Field(default_factory=list) #one task at a time?
    # load: float = 0.0 # not needed

class RuntimeVariables(BaseModel):
    """Temporary variables used during agent operations."""
    working_data: Dict[str, Any] = Field(default_factory=dict, description="Working data for the agent")
    temp_storage: Dict[str, Any] = Field(default_factory=dict, description="Temporary storage for the agent")
    cache: Dict[str, Any] = Field(default_factory=dict, description="Cache for the agent")
    counters: Dict[str, int] = Field(default_factory=dict, description="Counters for the agent")
    flags: Dict[str, bool] = Field(default_factory=dict, description="Flags for the agent")

class HistoryEntry(BaseModel):
    """Single entry in agent history."""
    message: Message = Field(default=None, description="Message", alias="message")
    timestamp: datetime = Field(default_factory=datetime.now, description="Timestamp of the message")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Metadata of the message")

class AgentSchema(BaseSchema, TimestampedSchema, MetadataSchema):
    """Base schema for agent data."""
    type: AgentType = Field(default=None, description="Type of the agent")
    name: Optional[str] = Field(default=None, description="Name of the agent")
    capabilities: Optional[List[str]] = Field(default=None, description="Capabilities of the agent")
    
    # State management
    agent_state: AgentState = Field(default_factory=AgentState, description="State of the agent")
    runtime_variables: RuntimeVariables = Field(default_factory=RuntimeVariables, description="Runtime variables of the agent")
    
    # History management
    max_history: int = Field(default=100, description="Maximum number of history entries to keep")
    history: List[HistoryEntry] = Field(default_factory=list, description="History of the agent")
    last_message: Optional[Message] = Field(default=None, description="Last message received by the agent")
    
    async def add_to_history(self, message: Any, **metadata) -> None:
        """Add message to history with metadata."""
        entry = HistoryEntry(
            message=message,
            metadata=metadata
        )
        self.history.append(entry)
        if len(self.history) > self.max_history:
            self.history.pop(0)
    
    async def update_state(self, **kwargs) -> None:
        """Update agent state with provided values."""
        for key, value in kwargs.items():
            if hasattr(self.agent_state, key):
                setattr(self.agent_state, key, value)

    async def set_variable(self, category: str, key: str, value: Any) -> None:
        """Set a variable in the specified category."""
        if hasattr(self.runtime_variables, category):
            getattr(self.runtime_variables, category)[key] = value

    async def get_variable(self, category: str, key: str) -> Optional[Any]:
        """Get a variable from the specified category."""
        if hasattr(self.runtime_variables, category):
            return getattr(self.runtime_variables, category).get(key)
        return None

    def get_summary(self) -> Dict[str, Any]:
        """Get a summary of current agent state."""
        return {
            "type": self.type,
            "name": self.name,
            "state": self.agent_state.model_dump(),
            "variables": self.runtime_variables.model_dump(),
            "history_count": len(self.history),
            "last_message": self.last_message.model_dump() if self.last_message else None,
            "metadata": self.metadata
        }

    async def get_history(
        self, 
        limit: Optional[int] = None, 
        message_type: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> List[HistoryEntry]:
        """Get filtered message history.
        
        Args:
            limit: Maximum number of entries to return
            message_type: Filter by message type
            start_time: Filter messages after this time
            end_time: Filter messages before this time
        """
        filtered = self.history

        if message_type:
            filtered = [h for h in filtered if getattr(h.message, "type", None) == message_type]
            
        if start_time:
            filtered = [h for h in filtered if h.timestamp >= start_time]
            
        if end_time:
            filtered = [h for h in filtered if h.timestamp <= end_time]
            
        if limit:
            filtered = filtered[-limit:]
            
        return filtered

    def get_state(self) -> Dict[str, Any]:
        """Get detailed current agent state."""
        return {
            "agent": {
                "type": self.type,
                "name": self.name,
                "capabilities": self.capabilities
            },
            "state": self.agent_state.model_dump(),
            "runtime": self.runtime_variables.model_dump(),
            "history": {
                "count": len(self.history),
                "last_message": self.last_message.model_dump() if self.last_message else None,
                "last_timestamp": self.history[-1].timestamp if self.history else None
            },
            "metadata": self.metadata,
            "timestamps": {
                "created_at": self.created_at,
                "updated_at": self.updated_at
            }
        }

    async def cleanup(self) -> None:
        """Clean up agent schema resources."""
        # Clear history
        self.history.clear()
        
        # Reset state
        self.agent_state = AgentState()
        
        # Clear runtime variables
        self.runtime_variables = RuntimeVariables()
        
        # Clear last message
        self.last_message = None
        
        # Reset metadata timestamps
        self.updated_at = datetime.now()
        
        # Keep created_at and other immutable metadata
        preserved_metadata = {
            "created_at": self.metadata.get("created_at"),
            "version": self.metadata.get("version"),
            "agent_id": self.metadata.get("agent_id")
        }
        
        # Reset metadata but preserve essential fields
        self.metadata = {
            k: v for k, v in preserved_metadata.items() 
            if v is not None
        }