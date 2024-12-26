from datetime import datetime
from enum import Enum
from typing import Dict, Any, Optional, List, Any
from pydantic import BaseModel, Field, ConfigDict, field_serializer
from uuid import UUID, uuid4

class MessagePriority(Enum):
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    CRITICAL = "critical"

class MessageStatus(Enum):
    PENDING = "pending"
    DELIVERED = "delivered"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    RETRYING = "retrying"

class Message(BaseModel):
    """Base message schema for inter-agent communication."""
    model_config = ConfigDict()

    id: UUID = Field(default_factory=uuid4)
    sender: str
    recipient: str
    message_type: str
    priority: MessagePriority = MessagePriority.NORMAL
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