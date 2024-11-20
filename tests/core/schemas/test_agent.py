import pytest
from pydantic import ValidationError
from core.schemas.agent import (
    AgentSchema,
    AgentStatus,
    AgentType
)

def test_agent_schema():
    """Test AgentSchema validation and defaults."""
    # Test minimal agent
    agent = AgentSchema(
        id="test-agent",
        name="Test Agent",
        type=AgentType.PROJECT_MANAGER
    )
    assert agent.id == "test-agent"
    assert agent.name == "Test Agent"
    assert agent.type == AgentType.PROJECT_MANAGER
    assert agent.status == AgentStatus.IDLE
    assert agent.capabilities == []
    assert agent.current_task is None
    assert agent.performance_metrics == {}

    # Test full agent configuration
    agent = AgentSchema(
        id="test-agent",
        name="Test Agent",
        type=AgentType.CODING,
        status=AgentStatus.BUSY,
        capabilities=["python", "testing"],
        current_task="task-123",
        performance_metrics={"accuracy": 0.95}
    )
    assert agent.status == AgentStatus.BUSY
    assert "python" in agent.capabilities
    assert agent.current_task == "task-123"
    assert agent.performance_metrics["accuracy"] == 0.95

def test_agent_status_validation():
    """Test AgentStatus validation."""
    # Test invalid status
    with pytest.raises(ValidationError):
        AgentSchema(
            id="test-agent",
            name="Test Agent",
            type=AgentType.PROJECT_MANAGER,
            status="invalid"
        )

def test_agent_type_validation():
    """Test AgentType validation."""
    # Test invalid type
    with pytest.raises(ValidationError):
        AgentSchema(
            id="test-agent",
            name="Test Agent",
            type="invalid"
        ) 