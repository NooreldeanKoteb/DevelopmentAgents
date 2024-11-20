from enum import Enum
from typing import Dict, Any, Optional
from datetime import datetime
from uuid import UUID, uuid4
from pydantic import Field

from .base import BaseSchema

class MessageType(str, Enum):
    """Message type enumeration."""
    TASK_CREATION = "task_creation"
    TASK_UPDATE = "task_update"
    TASK_COMPLETION = "task_completion"
    TASK_FAILURE = "task_failure"
    RESOURCE_ALLOCATION = "resource_allocation"
    RESOURCE_UPDATE = "resource_update"
    PROJECT_UPDATE = "project_update"
    STATUS_UPDATE = "status_update"
    ERROR = "error"
    INFO = "info"
    WARNING = "warning"
    QUERY = "query"
    RESPONSE = "response"
    COMMAND = "command"

class MessagePriority(str, Enum):
    """Message priority enumeration."""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    CRITICAL = "critical"

class MessageStatus(str, Enum):
    """Message status enumeration."""
    PENDING = "pending"
    DELIVERED = "delivered"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    RETRYING = "retrying"

class MessageSchema(BaseSchema):
    """Message schema definition."""
    id: UUID = Field(default_factory=uuid4)
    type: MessageType
    priority: MessagePriority = MessagePriority.NORMAL
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

    class Config:
        json_encoders = {
            UUID: str,
            datetime: lambda v: v.isoformat()
        } 