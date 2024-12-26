import pytest
from unittest.mock import MagicMock
from agents.base.base_agent import BaseAgent
from core.schemas.messages import MessageSchema, MessageType, MessageStatus
from core.schemas.enums import AgentType
from typing import Dict, Any
from datetime import datetime
import uuid

@pytest.fixture
def mock_metrics():
    """Create mock metrics."""
    metrics = MagicMock()
    metrics.message_count = MagicMock()
    metrics.message_count.inc = MagicMock()
    metrics.error_count = MagicMock()
    metrics.error_count.inc = MagicMock()
    metrics.error_types = MagicMock()
    metrics.error_types.labels = MagicMock(return_value=MagicMock())
    return metrics

def test_base_agent_instantiation():
    """Test that BaseAgent cannot be instantiated directly."""
    with pytest.raises(TypeError, match="Can't instantiate abstract class BaseAgent"):
        BaseAgent(
            agent_id="test-agent-1",
            name="Test Agent",
            agent_type=AgentType.PROJECT_MANAGER
        )

def test_incomplete_agent_instantiation():
    """Test that incomplete agent implementation cannot be instantiated."""
    class IncompleteAgent(BaseAgent):
        pass  # Missing required abstract methods
        
    with pytest.raises(TypeError, match="Can't instantiate abstract class IncompleteAgent with abstract method _handle_message_type"):
        IncompleteAgent(
            agent_id="test-agent-1",
            name="Test Agent",
            agent_type=AgentType.PROJECT_MANAGER
        )

@pytest.mark.asyncio
async def test_concrete_agent_implementation(mock_metrics):
    """Test that a concrete implementation works correctly."""
    class ConcreteAgent(BaseAgent):
        async def _handle_message_type(self, message: MessageSchema) -> Dict[str, Any]:
            return {"status": "handled", "message_id": message.id}

    agent = ConcreteAgent(
        agent_id="test-agent-1",
        name="Test Agent",
        agent_type=AgentType.PROJECT_MANAGER
    )
    agent.metrics = mock_metrics

    message = MessageSchema(
        id=str(uuid.uuid4()),
        type=MessageType.TASK_CREATION,
        status=MessageStatus.PENDING,
        content={"test": "value"},
        sender="test-sender",
        created_at=datetime.now()
    )

    result = await agent._handle_message_type(message)
    assert result["status"] == "handled"
    assert result["message_id"] == message.id