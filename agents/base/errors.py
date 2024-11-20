class AgentError(Exception):
    """Base exception for agent-related errors."""
    pass

class MemoryError(AgentError):
    """Base exception for memory-related errors."""
    pass

class MessageError(AgentError):
    """Base exception for message-related errors."""
    pass

class ContextError(AgentError):
    """Base exception for context-related errors."""
    pass

class TaskError(AgentError):
    """Base exception for task-related errors."""
    pass 