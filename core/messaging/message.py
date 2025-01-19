from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict, field_serializer
from uuid import uuid4
from typing import Any, Dict, Optional, List
from core.schemas.enums import Priority, MessageStatus, MessageType
from core.schemas.base import TimestampedSchema, ErrorSchema

class BaseMessage(TimestampedSchema, ErrorSchema):
    """Base message schema for communication."""
    model_config = ConfigDict()

class Message(BaseMessage):
    """Message schema for communication."""
    sender: str = Field(..., description="The sender of the message")
    recipient: str = Field(..., description="The recipient of the message")
    correlation_id: Optional[List[str]] = Field(None, description="ID linking related messages (e.g., request/response chain)")
    reply_to: Optional[str] = Field(None, description="ID of the message being replied to")

    type: MessageType = Field(..., description="The type of the message")
    status: MessageStatus = Field(MessageStatus.PENDING, description="The status of the message")
    priority: Priority = Field(Priority.UKNOWN, description="The priority of the message")
    
    topic: str = Field(..., description="The topic of the message")
    payload: Dict[str, Any] = Field(..., description="The payload of the message")
    
    retry_count: int = 0
    max_retries: int = 3
    
    @field_serializer('*', when_used='json')
    def serialize_datetime(self, value: Any, _info) -> Any:
        if isinstance(value, datetime):
            return value.isoformat()
        return value
    
    def __init__(self, **data):
        """Initialize message, preserving provided ID or generating new one."""
        if 'id' not in data:
            data['id'] = str(uuid4())
        super().__init__(**data)
    
    @classmethod
    def create(
        cls,
        sender: str,
        type: MessageType,
        priority: Priority,
        payload: Dict[str, Any],
        recipient: Optional[str] = None,
        correlation_ids: Optional[List[str]] = None,
        reply_to: Optional[str] = None,
        id: Optional[str] = None,
    ) -> "Message":
        """Create a new message with optional parameters.
        
        Args:
            sender: ID of the sending agent
            type: Type of message
            payload: The message payload
            recipient: ID of the recipient agent (optional)
            correlation_ids: List of related message IDs (optional)
            reply_to: ID of message being replied to (optional)
            priority: Message priority (defaults to NORMAL)
            id: Custom message ID (optional, will generate UUID if not provided)
        """
        return cls(
            id=id or str(uuid4()),
            sender=sender,
            recipient=recipient,
            type=type,
            payload=payload,
            correlation_ids=correlation_ids or [],
            reply_to=reply_to,
            priority=priority,
        ) 