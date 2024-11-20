import pytest
from unittest.mock import AsyncMock, patch
from datetime import datetime

from agents.base import BaseAgent, AgentError
from core.messaging import Message
from core.schemas import AgentType, AgentStatus

class TestAgent(BaseAgent):
    """Test agent implementation."""
    async def process_message(self, message):
        return Message(
            topic="response",
            content={"processed": message.content},
            sender=self.id
        )
        
    async def execute_task(self, task):
        return {"status": "completed", "result": task}

@pytest.fixture
async def agent():
    """Provide a test agent instance."""
    agent = TestAgent(
        name="TestAgent",
        agent_type=AgentType.PROJECT_MANAGER
    )
    await agent.initialize()
    yield agent
    await agent.stop()

@pytest.mark.asyncio
async def test_agent_initialization(agent):
    """Test agent initialization."""
    assert agent.id is not None
    assert agent.status == AgentStatus.IDLE
    assert agent.message_broker is not None
    assert agent.memory is not None
    assert agent.context is not None
    assert agent.logger is not None
    assert agent.metrics is not None

@pytest.mark.asyncio
async def test_message_processing(agent):
    """Test message processing pipeline."""
    test_message = Message(
        topic=f"agent.{agent.id}",
        content={"test": "data"},
        sender="test"
    )
    
    # Process message
    response = await agent._process_message(test_message)
    
    # Verify metrics
    assert agent.metrics.message_count._value.get() > 0
    assert agent.status == AgentStatus.IDLE

@pytest.mark.asyncio
async def test_agent_state(agent):
    """Test agent state management."""
    state = agent.get_state()
    assert state.id == agent.id
    assert state.name == "TestAgent"
    assert state.type == AgentType.PROJECT_MANAGER
    assert state.status == AgentStatus.IDLE

@pytest.mark.asyncio
async def test_agent_memory(agent):
    """Test agent memory operations."""
    # Store data
    await agent.save_to_memory("test_key", {"data": "test"})
    
    # Recall data
    data = await agent.recall_from_memory("test_key")
    assert data == {"data": "test"}

@pytest.mark.asyncio
async def test_error_handling(agent):
    """Test error handling."""
    with patch.object(agent, 'process_message', 
                     side_effect=Exception("Test error")):
        with pytest.raises(AgentError):
            await agent._process_message(
                Message(
                    topic="test",
                    content={},
                    sender="test"
                )
            )

@pytest.mark.asyncio
async def test_context_manager():
    """Test async context manager."""
    async with TestAgent() as agent:
        assert agent.status == AgentStatus.IDLE
        assert agent.message_broker is not None
    assert agent.status == AgentStatus.OFFLINE