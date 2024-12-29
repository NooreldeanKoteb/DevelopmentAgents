import pytest
from agents.base.errors import AgentError

def test_agent_error():
    """Test agent error hierarchy."""
    error = AgentError("Test error")
    assert isinstance(error, Exception)
    assert str(error) == "Test error" 