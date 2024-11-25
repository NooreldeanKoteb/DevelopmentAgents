import pytest
from unittest.mock import AsyncMock, MagicMock
import uuid
from datetime import datetime
from agents.base.base_agent import BaseAgent
from agents.base.message import Message
from core.monitoring import CoreLogger, CoreMetrics

@pytest.fixture
def mock_metrics():
    metrics = MagicMock()
    metrics.message_count = MagicMock()
    metrics.error_count = MagicMock()
    metrics.message_processing_time = MagicMock()
    metrics.message_processing_time.time = MagicMock()
    metrics.error_types = MagicMock()
    metrics.error_types.labels = MagicMock(return_value=MagicMock())
    return metrics

@pytest.fixture
def mock_logger():
    logger = MagicMock()
    logger.logger = MagicMock()
    return logger

class TestAgent(BaseAgent):
    """Test implementation of BaseAgent."""
    async def _handle_message_type(self, message):
        return "processed"

    async def handle_error(self, error):
        await super().handle_error(error)
        return "handled"

@pytest.mark.asyncio
async def test_agent_initialization():
    """Test agent initialization."""
    agent = TestAgent(
        agent_id="test",
        name="Test Agent",
        agent_type="test"
    )
    await agent.initialize()
    assert agent._initialized
    assert hasattr(agent, 'logger')
    assert hasattr(agent, 'metrics')
    assert hasattr(agent, 'memory')
    assert hasattr(agent, 'context')
    assert hasattr(agent, 'message_broker')

@pytest.mark.asyncio
async def test_message_processing(mock_metrics, mock_logger):
    """Test message processing."""
    agent = TestAgent(
        agent_id="test",
        name="Test Agent",
        agent_type="test"
    )
    agent.metrics = mock_metrics
    agent.logger = mock_logger
    await agent.initialize()
    
    message = Message(
        id=str(uuid.uuid4()),
        topic="test_topic",
        type="test_type",
        content="test message",
        sender="test_sender",
        timestamp=datetime.now(),
        payload={"test": "data"}
    )
    
    result = await agent.process_message(message)
    assert "processed" in str(result)
    mock_metrics.message_count.inc.assert_called_once()

@pytest.mark.asyncio
async def test_agent_state():
    """Test agent state management."""
    agent = TestAgent(
        agent_id="test",
        name="Test Agent",
        agent_type="test"
    )
    
    assert not hasattr(agent, '_initialized') or not agent._initialized
    await agent.initialize()
    assert agent._initialized
    
    await agent.cleanup()
    assert not agent._initialized

@pytest.mark.asyncio
async def test_agent_memory():
    """Test agent memory operations."""
    agent = TestAgent(
        agent_id="test",
        name="Test Agent",
        agent_type="test"
    )
    
    await agent.initialize()
    test_data = {"data": "test"}
    await agent.save_to_memory("test_key", test_data)
    retrieved_data = await agent.recall_from_memory("test_key")
    assert retrieved_data == test_data

@pytest.mark.asyncio
async def test_error_handling(mock_metrics, mock_logger):
    """Test error handling."""
    agent = TestAgent(
        agent_id="test",
        name="Test Agent",
        agent_type="test"
    )
    agent.metrics = mock_metrics
    agent.logger = mock_logger
    await agent.initialize()
    
    error = Exception("test error")
    result = await agent.handle_error(error)
    assert result == "handled"
    mock_metrics.error_count.inc.assert_called_once()
    mock_logger.logger.error.assert_called_once()