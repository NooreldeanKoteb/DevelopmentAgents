import pytest
import asyncio
from datetime import datetime
from typing import Dict, Any
from agents.base.base_agent import BaseAgent
from core.schemas.messages import MessageSchema, MessageType, MessageStatus
from core.schemas.enums import AgentType

@pytest.fixture
async def test_agent(redis_client):
    """Fixture to provide a test agent instance."""
    class TestAgent(BaseAgent):
        agent_type = AgentType.PROJECT_MANAGER

        async def process_message(self, message: MessageSchema) -> Dict[str, Any]:
            if not message.recipient:
                raise ValueError("Message must have a recipient")
            return {"status": "processed", "message_id": message.id}

        async def execute_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
            if "id" not in task:
                raise ValueError("Task must have an id")
            return {"status": "executed", "task_id": task.get("id")}

        async def handle_error(self, error: Exception) -> Dict[str, Any]:
            return {"status": "error_handled", "error": str(error)}

        async def _handle_message_type(self, message: MessageSchema) -> Dict[str, Any]:
            return {"status": "handled", "message_id": message.id}

        def get_metadata(self) -> Dict[str, Any]:
            return {
                "agent_type": self.agent_type,
                "agent_id": self.agent_id,
                "name": self.name
            }

        def get_status(self) -> Dict[str, Any]:
            return {
                "status": "active",
                "last_active": datetime.now(),
                "message_count": 0
            }

    return TestAgent(
        agent_id="test-agent-1",
        name="Test Agent",
        agent_type=AgentType.PROJECT_MANAGER,
        redis_client=redis_client
    )

@pytest.fixture
def test_message():
    """Fixture to provide a test message."""
    return MessageSchema(
        type=MessageType.TASK_CREATION,
        status=MessageStatus.PENDING,
        sender="test-sender",
        recipient="test-recipient",
        content={"action": "test"},
        created_at=datetime.now(),
        metadata={"test": "metadata"}
    )

@pytest.fixture
def test_task():
    """Fixture to provide a test task."""
    return {
        "id": "test-task-1",
        "type": "test",
        "description": "Test task",
        "parameters": {"param1": "value1"}
    }

@pytest.mark.asyncio
async def test_agent_initialization(test_agent):
    """Test agent initialization."""
    assert isinstance(test_agent, BaseAgent)
    assert test_agent.agent_type == AgentType.PROJECT_MANAGER

@pytest.mark.asyncio
async def test_process_message(test_agent, test_message):
    """Test message processing."""
    result = await test_agent.process_message(test_message)
    assert result["status"] == "processed"
    assert result["message_id"] == test_message.id

@pytest.mark.asyncio
async def test_execute_task(test_agent, test_task):
    """Test task execution."""
    result = await test_agent.execute_task(test_task)
    assert result["status"] == "executed"
    assert result["task_id"] == test_task["id"]

@pytest.mark.asyncio
async def test_handle_error(test_agent):
    """Test error handling."""
    test_error = Exception("Test error message")
    result = await test_agent.handle_error(test_error)
    assert result["status"] == "error_handled"
    assert result["error"] == "Test error message"

@pytest.mark.asyncio
async def test_message_validation(test_agent):
    """Test message validation."""
    invalid_message = MessageSchema(
        type=MessageType.TASK_CREATION,
        status=MessageStatus.PENDING,
        sender="test-sender",
        # Missing recipient field
        content={},
        created_at=datetime.now()
    )
    
    with pytest.raises(ValueError):
        await test_agent.process_message(invalid_message)

@pytest.mark.asyncio
async def test_task_validation(test_agent):
    """Test task validation."""
    invalid_task = {
        # Missing id field
        "type": "test",
        "description": "Invalid task"
    }
    
    with pytest.raises(ValueError):
        await test_agent.execute_task(invalid_task)

@pytest.mark.asyncio
async def test_agent_metadata(test_agent):
    """Test agent metadata handling."""
    metadata = test_agent.get_metadata()
    assert "agent_type" in metadata
    assert metadata["agent_type"] == AgentType.PROJECT_MANAGER

@pytest.mark.asyncio
async def test_agent_status(test_agent):
    """Test agent status."""
    status = test_agent.get_status()
    assert "status" in status
    assert "last_active" in status
    assert "message_count" in status

@pytest.mark.asyncio
async def test_complex_message_processing(test_agent, test_message):
    """Test processing of complex messages."""
    # Add complex data to message
    test_message.content = {
        "action": "complex_test",
        "parameters": {
            "nested": {
                "data": "value"
            },
            "array": [1, 2, 3],
            "timestamp": datetime.now().isoformat()
        }
    }
    
    result = await test_agent.process_message(test_message)
    assert result["status"] == "processed"
    assert result["message_id"] == test_message.id

@pytest.mark.asyncio
async def test_concurrent_tasks(test_agent, test_task):
    """Test handling multiple tasks concurrently."""
    tasks = [
        {**test_task, "id": f"task-{i}"} 
        for i in range(3)
    ]
    
    results = await asyncio.gather(
        *[test_agent.execute_task(task) for task in tasks]
    )
    
    assert len(results) == 3
    for i, result in enumerate(results):
        assert result["status"] == "executed"
        assert result["task_id"] == f"task-{i}"