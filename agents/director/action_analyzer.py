import re
from typing import Dict, Optional
from agents.director.enums import ActionType
from core.messaging.schemas import Message
class ActionAnalyzer:
    async def determine_action_type(self, message: Message) -> str:
        """Determine the type of action from a message."""
        # First check metadata override
        if "action_type" in message.metadata:
            return message.metadata["action_type"]
            
        # If message has an explicit type that matches our patterns, use it
        if message.type and message.type != "default":
            return message.type
            
        # Otherwise analyze content
        patterns = {
            "task_creation": ["create", "new task"],
            "task_update": ["update", "status"],
            "resource_allocation": ["allocate", "resource"],
            "error_handling": ["error", "failed"],
            "project_update": [".*"]  # Default catch-all
        }
        
        content = str(message.content).lower()
        for action_type, keywords in patterns.items():
            if any(keyword in content for keyword in keywords):
                return action_type
                
        return "project_update"