import pytest
from agents.base import BaseAgent

@pytest.fixture
def agent():
    """Provide a test agent instance."""
    return BaseAgent(
        agent_id="test-agent",
        name="Test Agent",
        agent_type="test"
    )

def test_agent_initialization(agent):
    """Test agent initialization."""
    assert agent.agent_id == "test-agent"
    assert agent.state is not None

def test_message_processing(agent):
    """Test message processing."""
    assert agent.process_message is not None

def test_agent_state(agent):
    """Test agent state management."""
    agent.update_state({"test": "value"})
    assert agent.state.get("test") == "value"

def test_agent_memory(agent):
    """Test agent memory operations."""
    assert agent.memory is not None

def test_error_handling(agent):
    """Test error handling."""
    with pytest.raises(NotImplementedError):
        agent.handle_error(Exception("test"))