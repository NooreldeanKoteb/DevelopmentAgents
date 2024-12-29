from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict, field_serializer
from uuid import uuid4
from typing import Any, Dict, Optional
from core.schemas.enums import Priority, MessageStatus, MessageType

class BaseMessage(BaseModel):
    """Base message schema for communication."""
    model_config = ConfigDict()

class ServiceMessage(BaseMessage):
    """Message model for inter-service communication."""
    id: str = Field(default_factory=lambda: str(uuid4()))
    topic: str
    content: Dict[str, Any]
    sender: str
    timestamp: datetime = Field(default_factory=datetime.now)
    recipient: Optional[str] = None
    correlation_id: Optional[str] = None
    reply_to: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    def __init__(self, **data):
        """Initialize message, preserving provided ID or generating new one."""
        if 'id' not in data:
            data['id'] = str(uuid4())
        super().__init__(**data)
    
    @classmethod
    def create(cls, topic: str, content: Dict[str, Any], sender: str, id: Optional[str] = None) -> "Message":
        """Create a new message with optional ID."""
        return cls(
            id=id or str(uuid4()),
            topic=topic,
            content=content,
            sender=sender
        ) 
    


#TOdo: figure this out
class AgentMessage(BaseMessage):
    """Base message schema for inter-agent communication."""

    id: UUID = Field(default_factory=uuid4)
    agent_id: str
    sender: str
    recipient: str
    type: MessageType
    content: Any
    priority: Priority = Priority.NORMAL
    payload: Dict[str, Any]
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    status: MessageStatus = MessageStatus.PENDING
    retry_count: int = 0
    max_retries: int = 3
    processed_at: Optional[datetime] = None
    error: Optional[Dict[str, Any]] = None

    @field_serializer('*', when_used='json')
    def serialize_datetime(self, value: Any, _info) -> Any:
        if isinstance(value, datetime):
            return value.isoformat()
        return value
    