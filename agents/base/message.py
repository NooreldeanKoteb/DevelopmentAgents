from typing import Dict, Any, Optional
from datetime import datetime
from pydantic import BaseModel, Field
import uuid
from .errors import MessageError

class Message(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    type: str = Field(...)
    content: Any
    metadata: Dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = datetime.utcnow()
    sender: Optional[str] = None
    recipient: Optional[str] = None 