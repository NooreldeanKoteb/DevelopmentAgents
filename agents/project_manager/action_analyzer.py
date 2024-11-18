import re
from typing import Dict, Optional
from agents.project_manager.enums import ActionType
from agents.base.message import Message

class ActionAnalyzer:
    def __init__(self):
        self.patterns = {
            ActionType.ERROR_HANDLING: r"error|failed|exception|crash|bug",
            ActionType.TASK_CREATION: r"create|new|add|start|initiate",
            ActionType.TASK_UPDATE: r"update|modify|change|edit|revise",
            ActionType.RESOURCE_ALLOCATION: r"assign|allocate|resource|worker|agent",
            ActionType.TIMELINE_UPDATE: r"schedule|timeline|deadline|date|delay",
            ActionType.PRIORITY_ADJUSTMENT: r"priority|urgent|important|critical",
            ActionType.DEPENDENCY_UPDATE: r"depends|dependency|blocking|blocked|prerequisite",
            ActionType.STATUS_CHANGE: r"status|complete|finish|done|progress"
        }

    def determine_action_type(self, message: Message) -> str:
        """Analyze message content to determine action type."""
        content = message.content.lower()
        metadata = message.metadata or {}
        
        # Check metadata first
        if "action_type" in metadata:
            return metadata["action_type"]
        
        # Check patterns
        for action_type, pattern in self.patterns.items():
            if re.search(pattern, content):
                return action_type.value
                
        return ActionType.PROJECT_UPDATE.value 