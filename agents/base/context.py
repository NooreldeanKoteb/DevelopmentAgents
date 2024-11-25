from typing import Dict, Any, Optional, List
from datetime import datetime
from core.messaging import Message
from .errors import ContextError

class Context:
    """Maintains agent context and state."""
    
    def __init__(self, max_history: int = 100):
        self.max_history = max_history
        self.history = []
        self.variables = {}
        self.state = {}
        self.last_message = None
        self.last_updated = datetime.utcnow()
        
    def get_history(self, limit: Optional[int] = None, topic: Optional[str] = None) -> List[Dict]:
        """Get message history with optional limit and topic filter."""
        filtered = self.history
        if topic:
            filtered = [h for h in filtered if getattr(h["message"], "topic", None) == topic]
        if limit:
            filtered = filtered[-limit:]
        return filtered
        
    def add_to_history(self, entry: Dict):
        self.history.append(entry)
        if len(self.history) > self.max_history:
            self.history.pop(0)
            
    def set_variable(self, key: str, value: Any):
        """Set a variable in context."""
        self.variables[key] = value
        
    def get_variable(self, key: str) -> Any:
        """Get a variable from context."""
        return self.variables.get(key)
        
    def clear(self) -> None:
        """Clear context state and history."""
        self.history = []
        self.variables = {}
        self.state = {}
        self.last_message = None
        self.last_updated = datetime.utcnow()
        
    def update(self, message: Message) -> None:
        """Update context with new message."""
        try:
            self.last_message = message
            self.last_updated = datetime.utcnow()
            
            # Update state based on message content
            if message.content:
                self.state.update(message.content)
                
            # Add to history
            self.add_to_history({
                "message": message,
                "timestamp": self.last_updated
            })
                
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
        """Clear context state and history."""
        self.history = []
        self.variables = {}
        self.state = {}
        self.last_message = None
        self.last_updated = datetime.utcnow() 