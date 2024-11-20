from typing import Dict, Any, Optional, List
from datetime import datetime
from collections import deque
from core.messaging import Message

class AgentContext:
    """Manages agent context and conversation history."""
    
    def __init__(self, max_history: int = 100):
        self.max_history = max_history
        self.history: deque = deque(maxlen=max_history)
        self.variables: Dict[str, Any] = {}
        self.last_update = datetime.now()
        
    def update(self, message: Message) -> None:
        """Update context with new message."""
        self.history.append({
            "message": message,
            "timestamp": datetime.now()
        })
        self.last_update = datetime.now()
        
    def get_history(
        self,
        limit: Optional[int] = None,
        topic: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get conversation history."""
        history = list(self.history)
        if topic:
            history = [
                h for h in history 
                if h["message"].topic == topic
            ]
        if limit:
            history = history[-limit:]
        return history
        
    def set_variable(self, key: str, value: Any) -> None:
        """Set context variable."""
        self.variables[key] = value
        self.last_update = datetime.now()
        
    def get_variable(self, key: str) -> Optional[Any]:
        """Get context variable."""
        return self.variables.get(key)
        
    def clear(self) -> None:
        """Clear context."""
        self.history.clear()
        self.variables.clear()
        self.last_update = datetime.now() 