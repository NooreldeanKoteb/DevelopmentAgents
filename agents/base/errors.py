class AgentError(Exception):
    """Base exception for agent errors."""
    pass

class MemoryError(AgentError):
    """Exception for memory-related errors."""
    pass

class ContextError(AgentError):
    """Exception for context-related errors."""
    pass

class MessageError(AgentError):
    """Exception for message processing errors."""
    pass

class TaskError(AgentError):
    """Exception for task execution errors."""
    pass 