from typing import Dict, Any, List, Optional
from .base import BaseSchema, SchemaVersion

class AgentMessageSchema(BaseSchema):
    """Schema for agent messages."""
    agent_id: str
    message_type: str
    content: Dict[str, Any]
    metadata: Optional[Dict[str, Any]] = None

class TaskSchema(BaseSchema):
    """Schema for tasks."""
    task_id: str
    task_type: str
    priority: int
    parameters: Dict[str, Any]
    dependencies: List[str] = []

class ResultSchema(BaseSchema):
    """Schema for task results."""
    task_id: str
    status: str
    result: Dict[str, Any]
    error: Optional[Dict[str, Any]] = None 