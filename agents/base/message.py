from typing import Dict, Any, Optional
from datetime import datetime
from pydantic import BaseModel

class Message(BaseModel):
    id: str
    content: str
    metadata: Optional[Dict[str, Any]] = None
    timestamp: datetime = datetime.utcnow()
    sender: Optional[str] = None
    recipient: Optional[str] = None 