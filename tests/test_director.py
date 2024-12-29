from unittest.mock import AsyncMock, MagicMock
import pytest
from datetime import datetime
from agents.director.agent import DirectorAgent
from agents.base.message import Message
from agents.director.planner import ProjectPlanner
from agents.director.enums import TaskStatus, TaskPriority, BusinessImpact
from agents.director.models import TaskSchema

@pytest.fixture
def sample_message():
    """Provide a sample message for testing."""
    return {
        "type": "task.create",
        "content": {
            "name": "Test Task",
            "description": "Test Description",
            "priority": TaskPriority.HIGH,
            "business_impact": BusinessImpact.MEDIUM,
            "estimated_duration": 2.0,
            "phase": "phase-1"
        }
    }

@pytest.fixture
async def Director(redis_client, task_manager, resource_manager):
    """Create a Director agent for testing."""
    agent = DirectorAgent(
        name="Test Director",
        agent_type="director",
        task_service=task_manager,
        resource_service=resource_manager,
        planner_service=None,  # Set to None since we'll create it after agent initialization
        redis_client=redis_client
    )
    # Initialize the planner after agent creation
    agent.planner_service = ProjectPlanner(agent=agent)
    return agent

@pytest.mark.asyncio
async def test_process_message(sample_message, redis_client):
    """Test Director message processing."""
    # Create async mocks
    mock_task_manager = AsyncMock()
    mock_planner = AsyncMock()
    mock_resource_manager = AsyncMock()
    
    # Mock metrics
    mock_metrics = MagicMock()
    mock_metrics.message_count = MagicMock()
    mock_metrics.error_count = MagicMock()
    mock_metrics.message_processing_time = MagicMock()
    mock_metrics.message_processing_time.time = MagicMock()
    mock_metrics.error_types = MagicMock()
    mock_metrics.error_types.labels = MagicMock(return_value=MagicMock())
    
    # Configure mock returns
    mock_task_manager.create_task.return_value = TaskSchema(
        id="test-task",
        name="Test Task",
        description="Test Description",
        status=TaskStatus.PENDING,
        priority=TaskPriority.HIGH,
        phase="phase-1",
    )
    mock_planner.generate_timeline.return_value = {}
    mock_resource_manager.get_resources.return_value = []
    
    agent = DirectorAgent(
        name="Test Director",
        agent_type="Director",
        task_service=mock_task_manager,
        resource_service=mock_resource_manager,
        planner_service=mock_planner,
        redis_client=redis_client
    )
    
    # Set mocked metrics
    agent.metrics = mock_metrics
    
    await agent.initialize()
    
    message = Message(
        type=sample_message["type"],
        content=sample_message["content"]
    )
    
    try:
        response = await agent.process_message(message)
        assert response.content["action_type"] == "task_creation"
        assert "task" in response.content
        assert "resources" in response.content
        assert "timeline" in response.content
    finally:
        await agent.cleanup()
 