import pytest
from agents.base.errors import (
    AgentError,
    MemoryError,
    ContextError,
    MessageError,
    TaskError
)

def test_agent_error():
    """Test agent error hierarchy."""
    error = AgentError("Test error")
    assert isinstance(error, Exception)
    assert str(error) == "Test error"

def test_memory_error():
    """Test memory error."""
    error = MemoryError("Memory test error")
    assert isinstance(error, AgentError)
    assert str(error) == "Memory test error"

def test_context_error():
    """Test context error."""
    error = ContextError("Context test error")
    assert isinstance(error, AgentError)
    assert str(error) == "Context test error"

def test_message_error():
    """Test message error."""
    error = MessageError("Message test error")
    assert isinstance(error, AgentError)
    assert str(error) == "Message test error"

def test_task_error():
    """Test task error."""
    error = TaskError("Task test error")
    assert isinstance(error, AgentError)
    assert str(error) == "Task test error" 