from typing import Dict, Any, Optional, List
from datetime import datetime
from core.messaging import Message
from .errors import ContextError

class Context:
    """Maintains agent context and state."""
    
    def __init__(self, max_history: int = 100):
        self.max_history = max_history
        self._history = []
        self._variables = {}
        
    def get_history(self) -> List[Dict]:
        return self._history
        
    def add_to_history(self, entry: Dict):
        self._history.append(entry)
        if len(self._history) > self.max_history:
            self._history.pop(0)
            
    def set_variable(self, key: str, value: Any):
        self._variables[key] = value
        
    def get_variable(self, key: str) -> Any:
        return self._variables.get(key)
        
    def clear(self):
        self._history.clear()
        self._variables.clear()
        
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