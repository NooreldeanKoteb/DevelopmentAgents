from datetime import datetime
from enum import Enum
from typing import Dict, Any, Optional, List, Any
from pydantic import BaseModel, Field, ConfigDict, field_serializer
from uuid import UUID, uuid4
from core.schemas.enums import Priority, MessageStatus
from core.schemas.base import BaseSchema


#TOdo: figure this out
class Message(BaseModel):
    """Base message schema for inter-agent communication."""
    model_config = ConfigDict()

    id: UUID = Field(default_factory=uuid4)
    sender: str
    recipient: str
    message_type: str
    priority: Priority = Priority.NORMAL
    payload: Dict[str, Any]
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    status: MessageStatus = MessageStatus.PENDING
    retry_count: int = 0
    max_retries: int = 3

    @field_serializer('*', when_used='json')
    def serialize_datetime(self, value: Any, _info) -> Any:
        if isinstance(value, datetime):
            return value.isoformat()
        return value
    

    class Message(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    type: str = Field(...)
    content: Any
    metadata: Dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = datetime.utcnow()
    sender: Optional[str] = None
    recipient: Optional[str] = None 


# Check these and refactor
class AgentMessageSchema(BaseModel):
    """Schema for agent messages."""
    agent_id: str
    message_type: str
    content: Dict[str, Any]
    metadata: Optional[Dict[str, Any]] = None




class MessageSchema(BaseSchema):
    """Message schema definition."""
    model_config = ConfigDict()

    id: UUID = Field(default_factory=uuid4)
    type: MessageType
    priority: Priority = Priority.NORMAL
    status: MessageStatus = MessageStatus.PENDING
    sender: str
    recipient: Optional[str] = None
    content: Dict[str, Any] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    processed_at: Optional[datetime] = None
    retry_count: int = 0
    max_retries: int = 3
    error: Optional[Dict[str, Any]] = None

    @field_serializer('*', when_used='json')
    def serialize_datetime(self, value: Any, _info) -> Any:
        if isinstance(value, datetime):
            return value.isoformat()
        return value