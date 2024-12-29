import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from agents.director.agent import DirectorAgent
from agents.base.schemas import Message
from core.messaging.message import Message as CoreMessage
from core.schemas.enums import ResourceStatus, Status, Priority
from core.schemas import ResourceSchema
from agents.director.schemas import TaskSchema
from agents.base.enums import AgentType
import json

@pytest.fixture
def mock_memory():
    """Create mock memory system."""
    memory = MagicMock()
    memory.initialize = AsyncMock()
    # Add store method (used by save_to_memory)
    memory.store = AsyncMock()
    # Add cleanup method
    memory.cleanup = AsyncMock()
    # Return JSON-encoded string for get/retrieve
    memory.get = AsyncMock(return_value=json.dumps({
        "spec": {
            "id": "test-project",
            "name": "Test Project"
        },
        "plan": {
            "phases": []
        },
        "tasks": [],
        "resources": []
    }))
    memory.retrieve = AsyncMock(return_value=json.dumps({
        "spec": {
            "id": "test-project",
            "name": "Test Project"
        },
        "plan": {
            "phases": []
        },
        "tasks": [],
        "resources": []
    }))
    memory.set = AsyncMock()
    memory.delete = AsyncMock()
    memory.list_memories = AsyncMock(return_value=[])
    return memory

@pytest.fixture
def mock_redis_client():
    """Create mock Redis client."""
    client = MagicMock()
    client.ping = AsyncMock()
    client.get = AsyncMock()
    client.set = AsyncMock()
    client.delete = AsyncMock()
    client.exists = AsyncMock(return_value=False)
    return client

@pytest.fixture
def mock_task_service():
    """Create mock task service."""
    service = MagicMock()
    # Mock both create_task and create_tasks
    service.create_task = AsyncMock(return_value={
        "id": "test-task",
        "name": "Test Task",
        "status": Status.PENDING,
        "description": "Test Description",
        "priority": Priority.HIGH,
        "estimated_duration": 2.0,
        "dependencies": []
    })
    service.create_tasks = AsyncMock(return_value=[{
        "id": "test-task",
        "name": "Test Task",
        "status": Status.PENDING,
        "description": "Test Description",
        "priority": Priority.HIGH,
        "estimated_duration": 2.0,
        "dependencies": []
    }])
    service.get_tasks = AsyncMock(return_value=[])
    service.update_task = AsyncMock()
    service.initialize = AsyncMock()
    return service

@pytest.fixture
def mock_resource_service():
    """Create mock resource service."""
    service = MagicMock()
    service.get_resources = AsyncMock(return_value=[])
    service.allocate_resources = AsyncMock(return_value={
        "allocated": True,
        "resources": []
    })
    service.update_resource_status = AsyncMock()
    service.update_agent_status = AsyncMock()
    service.reallocate_resources = AsyncMock()
    service.initialize = AsyncMock()
    return service

@pytest.fixture
def mock_planner_service():
    """Create mock planner service."""
    service = MagicMock()
    # Return dict instead of AsyncMock for create_plan
    service.create_plan = AsyncMock(return_value={
        "id": "test-project",
        "name": "Test Project",
        "phases": [
            {
                "id": "phase-1",
                "name": "Planning",
                "tasks": []
            }
        ],
        "dependencies": [],
        "estimated_duration": 10,
        "critical_path": ["phase-1"],
        "risk_assessment": {
            "level": "LOW",
            "factors": []
        }
    })
    # Return dict instead of AsyncMock for generate_timeline
    service.generate_timeline = AsyncMock(return_value={
        "timeline": [],
        "duration": 10
    })
    service.initialize = AsyncMock()
    return service

@pytest.fixture
def mock_metrics():
    metrics = MagicMock()
    metrics.message_count = MagicMock()
    metrics.error_count = MagicMock()
    metrics.error_count.inc = MagicMock()
    metrics.message_processing_time = MagicMock()
    return metrics

@pytest.fixture
async def agent(mock_redis_client, mock_task_service, mock_resource_service, mock_planner_service, mock_metrics, mock_memory):
    """Create a test agent with mocked dependencies."""
    with patch('agents.Director.agent.ProjectPlanner', return_value=mock_planner_service):
        agent = DirectorAgent(
            name="test_agent",
            agent_type="director",
            task_service=mock_task_service,
            resource_service=mock_resource_service,
            planner_service=mock_planner_service,
            redis_client=mock_redis_client
        )
        agent.metrics = mock_metrics
        agent.planner = mock_planner_service
        agent.resource_manager = mock_resource_service
        agent.task_service = mock_task_service
        agent.memory = mock_memory
        await agent.initialize()
        return agent

@pytest.mark.asyncio
async def test_initialize(agent):
    """Test agent initialization."""
    assert agent.name == "test_agent"
    assert agent.planner is not None
    assert agent.resource_manager is not None

@pytest.mark.asyncio
async def test_handle_task_creation(agent):
    """Test handling task creation."""
    task_data = {
        "id": "test-task",
        "name": "Test Task",
        "status": Status.PENDING,
        "description": "Test Description",
        "priority": Priority.HIGH,
        "estimated_duration": 2.0,
        "dependencies": []
    }
    message = Message(
        type="task.create",
        content=task_data,
        sender="test"
    )
    
    response = await agent._handle_task_creation(message)
    
    assert response.type == "task.created"
    agent.task_service.create_task.assert_called_once_with(task_data)
    agent.resource_service.get_resources.assert_called_once()
    agent.planner.generate_timeline.assert_called_once()

@pytest.mark.asyncio
async def test_handle_new_project(agent):
    """Test handling new project creation."""
    project_data = {
        "id": "test-project",
        "name": "Test Project",
        "description": "Test Description",
        "requirements": {},
        "priority": Priority.HIGH,
        "estimated_duration": 10.0,
        "dependencies": []
    }
    message = CoreMessage(
        topic="project.new",
        content=project_data,
        sender="test"
    )
    response = await agent._handle_new_project(message)
    assert response is not None
    agent.planner.create_plan.assert_called_once()

@pytest.mark.asyncio
async def test_handle_agent_status(agent):
    """Test handling agent status updates."""
    message = CoreMessage(
        topic="agent.status",
        content={
            "agent_id": "test-agent",
            "status": "active",
            "capabilities": ["coding", "testing"]
        },
        sender="test"
    )
    await agent._handle_agent_status(message)
    agent.resource_manager.update_agent_status.assert_called_once_with(
        "test-agent", "active"
    )

@pytest.mark.asyncio
async def test_handle_resource_status(agent):
    """Test handling resource status updates."""
    message = CoreMessage(
        topic="resource.status",
        content={
            "resource_id": "test-resource",
            "status": ResourceStatus.AVAILABLE,
            "type": "compute",
            "capacity": 100
        },
        sender="test"
    )
    await agent._handle_resource_status(message)
    agent.resource_manager.update_resource_status.assert_called_once()

@pytest.mark.asyncio
async def test_execute_task(agent):
    """Test task execution."""
    task = {
        "type": "create_project",
        "project_spec": {
            "id": "test-project",
            "name": "Test Project",
            "description": "Test Description",
            "requirements": {},
            "priority": Priority.HIGH,
            "estimated_duration": 10.0,
            "dependencies": []
        }
    }
    await agent.execute_task(task)
    agent.planner.create_plan.assert_called_once()

@pytest.mark.asyncio
async def test_handle_error(agent):
    """Test error handling."""
    error = Exception("Test error")
    await agent.handle_error(error)
    agent.metrics.error_count.inc.assert_called_once()

@pytest.mark.asyncio
async def test_invalid_message_type(agent):
    """Test handling invalid message type."""
    message = CoreMessage(
        topic="invalid.topic",
        content={},
        sender="test"
    )
    
    with pytest.raises(Exception):
        await agent._handle_message_type(message)

@pytest.mark.asyncio
async def test_handle_project_update(agent):
    """Test handling project updates."""
    update_data = {
        "project_id": "test-project",
        "type": "status_update",
        "status": "in_progress",
        "updates": {
            "progress": 50,
            "current_phase": "development"
        }
    }
    message = CoreMessage(
        topic="project.update",
        content=update_data,
        sender="test"
    )
    
    response = await agent._handle_project_update(message)
    assert response.topic == "project.updated"
    assert response.content["project_id"] == "test-project"

@pytest.mark.asyncio
async def test_save_to_memory(agent):
    """Test saving data to memory."""
    key = "test:key"
    data = {"test": "data"}
    await agent.save_to_memory(key, data)
    agent.memory.store.assert_called_once_with(key, data)  # Assert store was called

@pytest.mark.asyncio
async def test_get_active_projects(agent):
    """Test getting active projects."""
    projects = await agent._get_active_projects()
    assert isinstance(projects, list)

@pytest.mark.asyncio
async def test_handle_error(agent):
    """Test error handling."""
    error = Exception("Test error")
    await agent.handle_error(error)
    agent.metrics.error_count.inc.assert_called_once()

@pytest.mark.asyncio
async def test_cleanup(agent):
    """Test agent cleanup."""
    await agent.cleanup()
    agent.memory.cleanup.assert_called_once()  # Assert cleanup was called

@pytest.mark.asyncio
async def test_invalid_message_type(agent):
    """Test handling invalid message type."""
    message = CoreMessage(
        topic="invalid.topic",
        content={},
        sender="test"
    )
    
    with pytest.raises(Exception):
        await agent._handle_message_type(message) 