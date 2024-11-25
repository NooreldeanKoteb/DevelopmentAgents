from datetime import datetime
from pydantic import BaseModel, Field
from uuid import uuid4
from typing import Any, Dict, Optional

class Message(BaseModel):
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