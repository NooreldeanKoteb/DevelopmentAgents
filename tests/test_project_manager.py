from unittest.mock import AsyncMock
import pytest
from datetime import datetime
from agents.project_manager.agent import ProjectManagerAgent
from core.schemas import TaskSchema
from core.schemas.enums import TaskStatus, TaskPriority, BusinessImpact
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
        priority=TaskPriority.HIGH,
        business_impact=BusinessImpact.MEDIUM,
        estimated_duration=2.0,
        phase="phase-1",
        dependencies=[]
    )
    mock_planner.generate_timeline.return_value = {}
    mock_resource_manager.get_resources.return_value = []
    
    agent = ProjectManagerAgent(
        name="Test Project Manager",
        agent_type="project_manager",
        task_service=mock_task_manager,
        resource_service=mock_resource_manager,
        planner_service=mock_planner
    )
    
    message = Message(
        type=sample_message["type"],
        content=sample_message["content"]
    )
    
    response = await agent.process_message(message)
    assert response.action_type == "task_creation"
 