from typing import Dict, Any, Optional
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict
import uuid

class Message(BaseModel):
    """Represents a message in the system."""
    
    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        validate_assignment=True,
        extra='forbid'
    )
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    topic: str
    content: Dict[str, Any]
    sender: str
    recipient: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.now)
    correlation_id: Optional[str] = None
    reply_to: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict) 