from typing import Dict, Any, Optional
from datetime import datetime
from core.messaging import Message
from .errors import ContextError

class Context:
    """Maintains agent context and state."""
    
    def __init__(self):
        self.state: Dict[str, Any] = {}
        self.last_message: Optional[Message] = None
        self.last_updated = datetime.utcnow()
        
    def update(self, message: Message) -> None:
        """Update context with new message."""
        try:
            self.last_message = message
            self.last_updated = datetime.utcnow()
            
            # Update state based on message content
            if message.content:
                self.state.update(message.content)
                
        except Exception as e:
            raise ContextError(f"Failed to update context: {str(e)}")
            
    def get_state(self) -> Dict[str, Any]:
        """Get current context state."""
        return {
            "state": self.state,
            "last_message": self.last_message.model_dump() if self.last_message else None,
            "last_updated": self.last_updated.isoformat()
        }
        
    def clear(self) -> None:
        """Clear context state."""
        self.state = {}
        self.last_message = None
        self.last_updated = datetime.utcnow() 