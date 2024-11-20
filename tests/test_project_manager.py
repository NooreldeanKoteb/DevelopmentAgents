from unittest.mock import AsyncMock
import pytest
from agents.project_manager.agent import ProjectManagerAgent
from agents.project_manager.models import TaskSchema
from agents.project_manager.enums import TaskStatus, Priority, BusinessImpact
from agents.base.message import Message

@pytest.mark.asyncio
async def test_process_message(sample_message):
    """Test project manager message processing."""
    # Create async mocks
    mock_task_manager = AsyncMock()
    mock_planner = AsyncMock()
    mock_resource_manager = AsyncMock()
    
    # Configure mock returns
    mock_task_manager.create_task.return_value = TaskSchema(
        id="test-task",
        name="Test Task",
        description="Test Description",
        status=TaskStatus.PENDING,
        priority=Priority.HIGH,
        business_impact=BusinessImpact.MEDIUM,
        estimated_duration="2.0",
        phase="phase-1",
        dependencies=[]
    )
    mock_planner.generate_timeline.return_value = {}
    mock_resource_manager.get_resources.return_value = []
    
    agent = ProjectManagerAgent(
        task_manager=mock_task_manager,
        resource_manager=mock_resource_manager,
        planner=mock_planner
    )
    
    message = Message(
        type=sample_message["type"],
        content=sample_message["content"]
    )
    
    response = await agent.process_message(message)
    assert response.action_type == "task_creation"
 