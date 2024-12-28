import pytest
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock
from core.schemas import TaskSchema, TaskStatus, TaskPriority, BusinessImpact
from agents.director.task_manager import TaskManager
from agents.director.persistence import PersistenceManager
from agents.director.errors import TaskManagementError

@pytest.fixture
def persistence_manager():
    manager = MagicMock(spec=PersistenceManager)
    manager.get_all_tasks = AsyncMock(return_value=[])
    manager.save_task = AsyncMock()
    manager.get_task = AsyncMock()
    manager.delete_task = AsyncMock()
    return manager

@pytest.fixture
def task_manager(persistence_manager):
    return TaskManager(persistence_manager)

@pytest.mark.asyncio
async def test_get_tasks(task_manager, persistence_manager):
    """Test retrieving all tasks."""
    mock_tasks = [
        {"id": "task-1", "name": "Test Task 1"},
        {"id": "task-2", "name": "Test Task 2"}
    ]
    persistence_manager.get_all_tasks.return_value = mock_tasks
    
    tasks = await task_manager.get_tasks()
    assert tasks == mock_tasks
    persistence_manager.get_all_tasks.assert_called_once()

@pytest.mark.asyncio
async def test_add_task(task_manager):
    """Test adding a new task."""
    task_data = {
        "id": "task-1",
        "name": "Test Task",
        "description": "Test Description",
        "status": TaskStatus.PENDING,
        "priority": TaskPriority.HIGH,
        "business_impact": BusinessImpact.MEDIUM,
        "estimated_duration": 2.0,
        "dependencies": []
    }
    
    task = await task_manager.add_task(task_data)
    assert isinstance(task, TaskSchema)
    assert task.name == "Test Task"
    assert task.created_at is not None
    assert task.updated_at is not None

@pytest.mark.asyncio
async def test_update_task(task_manager, persistence_manager):
    """Test updating an existing task."""
    existing_task = TaskSchema(
        id="task-1",
        name="Original Name",
        description="Original Description",
        status=TaskStatus.PENDING,
        priority=TaskPriority.HIGH,
        business_impact=BusinessImpact.MEDIUM,
        estimated_duration=2.0,
        dependencies=[]
    )
    persistence_manager.get_task.return_value = existing_task
    
    updates = {"name": "Updated Name"}
    updated_task = await task_manager.update_task("task-1", updates)
    
    assert updated_task.name == "Updated Name"
    assert updated_task.updated_at > existing_task.updated_at

@pytest.mark.asyncio
async def test_update_task_not_found(task_manager, persistence_manager):
    """Test updating a non-existent task."""
    persistence_manager.get_task.return_value = None
    
    with pytest.raises(ValueError, match="Task task-1 not found"):
        await task_manager.update_task("task-1", {"name": "New Name"})

@pytest.mark.asyncio
async def test_create_tasks_from_plan(task_manager):
    """Test creating tasks from a project plan."""
    plan = {
        "phases": [
            {
                "name": "Phase 1",
                "tasks": [
                    {
                        "name": "Task 1",
                        "description": "Description 1",
                        "estimated_duration": 2.0,
                        "critical": True,
                        "business_impact": "HIGH"
                    },
                    {
                        "name": "Task 2",
                        "description": "Description 2",
                        "estimated_duration": 3.0,
                        "high_priority": True,
                        "business_impact": "MEDIUM",
                        "dependencies": ["task-1"]
                    }
                ]
            }
        ]
    }
    
    tasks = await task_manager.create_tasks(plan)
    assert len(tasks) == 2
    assert tasks[0].priority == TaskPriority.CRITICAL
    assert tasks[1].priority == TaskPriority.HIGH

@pytest.mark.asyncio
async def test_update_tasks_with_plan(task_manager):
    """Test updating tasks based on plan changes."""
    current_tasks = [
        TaskSchema(
            id="task-1",
            name="Original Task",
            description="Original Description",
            status=TaskStatus.PENDING,
            priority=TaskPriority.HIGH,
            business_impact=BusinessImpact.MEDIUM,
            estimated_duration=2.0,
            dependencies=[],
            phase="Phase 1"
        )
    ]
    
    updated_plan = {
        "phases": [
            {
                "name": "Phase 1",
                "tasks": [
                    {
                        "id": "task-1",
                        "name": "Updated Task",
                        "description": "Updated Description",
                        "estimated_duration": 3.0,
                        "business_impact": "MEDIUM",
                        "dependencies": ["task-2"]
                    }
                ]
            }
        ]
    }
    
    updated_tasks = await task_manager.update_tasks(current_tasks, updated_plan)
    assert len(updated_tasks) == 1
    assert updated_tasks[0].name == "Updated Task"
    assert updated_tasks[0].description == "Updated Description"

@pytest.mark.asyncio
async def test_update_task_status_with_dependencies(task_manager):
    """Test updating task status and dependency management."""
    tasks = [
        TaskSchema(
            id="task-1",
            name="Task 1",
            description="Description 1",
            status=TaskStatus.PENDING,
            priority=TaskPriority.HIGH,
            business_impact=BusinessImpact.MEDIUM,
            estimated_duration=2.0,
            dependencies=[]
        ),
        TaskSchema(
            id="task-2",
            name="Task 2",
            description="Description 2",
            status=TaskStatus.BLOCKED,
            priority=TaskPriority.HIGH,
            business_impact=BusinessImpact.MEDIUM,
            estimated_duration=3.0,
            dependencies=["task-1"]
        )
    ]
    
    updated_tasks = await task_manager.update_task_status(
        tasks,
        "task-1",
        TaskStatus.COMPLETED
    )
    
    assert len(updated_tasks) == 2
    assert updated_tasks[0].status == TaskStatus.COMPLETED
    assert updated_tasks[1].status == TaskStatus.PENDING

@pytest.mark.asyncio
async def test_update_task_status_not_found(task_manager):
    """Test updating status of non-existent task."""
    tasks = [
        TaskSchema(
            id="task-1",
            name="Task 1",
            description="Description 1",
            status=TaskStatus.PENDING,
            priority=TaskPriority.HIGH,
            business_impact=BusinessImpact.MEDIUM,
            estimated_duration=2.0,
            dependencies=[]
        )
    ]
    result = await task_manager.update_task_status(tasks, "invalid-id", TaskStatus.COMPLETED)
    assert len(result) == 1
    assert result[0].status == TaskStatus.PENDING

@pytest.mark.asyncio
async def test_determine_priority(task_manager):
    """Test priority determination logic."""
    assert task_manager._determine_priority({"critical": True}) == TaskPriority.CRITICAL
    assert task_manager._determine_priority({"high_priority": True}) == TaskPriority.HIGH
    assert task_manager._determine_priority({"low_priority": True}) == TaskPriority.LOW
    assert task_manager._determine_priority({}) == TaskPriority.MEDIUM 

@pytest.mark.asyncio
async def test_get_tasks_by_id_not_found(task_manager):
    """Test getting a task by ID that doesn't exist."""
    with pytest.raises(ValueError, match="Task invalid-id not found"):
        await task_manager.get_task_by_id("invalid-id")

@pytest.mark.asyncio
async def test_delete_task_not_found(task_manager):
    """Test deleting a task that doesn't exist."""
    with pytest.raises(ValueError, match="Task invalid-id not found"):
        await task_manager.delete_task("invalid-id")

@pytest.mark.asyncio
async def test_get_tasks_by_status(task_manager):
    """Test getting tasks by status."""
    # Create test tasks with different statuses
    task1 = TaskSchema(
        id="task-1",
        name="Task 1",
        description="Description 1",
        status=TaskStatus.PENDING,
        priority=TaskPriority.HIGH,
        business_impact=BusinessImpact.MEDIUM,
        estimated_duration=2.0
    )
    task2 = TaskSchema(
        id="task-2",
        name="Task 2",
        description="Description 2",
        status=TaskStatus.IN_PROGRESS,
        priority=TaskPriority.MEDIUM,
        business_impact=BusinessImpact.LOW,
        estimated_duration=1.0
    )
    
    task_manager.tasks = {
        task1.id: task1,
        task2.id: task2
    }
    
    pending_tasks = await task_manager.get_tasks_by_status(TaskStatus.PENDING)
    assert len(pending_tasks) == 1
    assert pending_tasks[0].id == "task-1"

@pytest.mark.asyncio
async def test_get_tasks_by_agent(task_manager):
    """Test getting tasks by agent."""
    # Create test tasks assigned to different agents
    task1 = TaskSchema(
        id="task-1",
        name="Task 1",
        description="Description 1",
        status=TaskStatus.PENDING,
        priority=TaskPriority.HIGH,
        business_impact=BusinessImpact.MEDIUM,
        estimated_duration=2.0,
        assigned_to="agent-1"
    )
    task2 = TaskSchema(
        id="task-2",
        name="Task 2",
        description="Description 2",
        status=TaskStatus.IN_PROGRESS,
        priority=TaskPriority.MEDIUM,
        business_impact=BusinessImpact.LOW,
        estimated_duration=1.0,
        assigned_to="agent-2"
    )
    
    task_manager.tasks = {
        task1.id: task1,
        task2.id: task2
    }
    
    agent_tasks = await task_manager.get_tasks_by_agent("agent-1")
    assert len(agent_tasks) == 1
    assert agent_tasks[0].id == "task-1"

@pytest.mark.asyncio
async def test_update_task_status_not_found(task_manager):
    """Test updating status of non-existent task."""
    tasks = [
        TaskSchema(
            id="task-1",
            name="Task 1",
            description="Description 1",
            status=TaskStatus.PENDING,
            priority=TaskPriority.HIGH,
            business_impact=BusinessImpact.MEDIUM,
            estimated_duration=2.0,
            dependencies=[]
        )
    ]
    result = await task_manager.update_task_status(tasks, "invalid-id", TaskStatus.COMPLETED)
    assert len(result) == 1
    assert result[0].status == TaskStatus.PENDING

@pytest.mark.asyncio
async def test_create_tasks_error(task_manager):
    """Test error handling in create_tasks."""
    invalid_plan = {
        "phases": [
            {
                "name": "Phase 1",
                "tasks": [
                    {
                        # Missing required fields
                        "name": "Task 1"
                    }
                ]
            }
        ]
    }
    
    with pytest.raises(TaskManagementError):
        await task_manager.create_tasks(invalid_plan)

@pytest.mark.asyncio
async def test_update_tasks_error(task_manager):
    """Test error handling in update_tasks."""
    current_tasks = [
        TaskSchema(
            id="task-1",
            name="Task 1",
            description="Description 1",
            status=TaskStatus.PENDING,
            priority=TaskPriority.HIGH,
            business_impact=BusinessImpact.MEDIUM,
            estimated_duration=2.0
        )
    ]
    
    invalid_plan = {
        "phases": [
            {
                "name": "Phase 1",
                "tasks": [
                    {
                        # Missing required fields
                        "id": "task-1"
                    }
                ]
            }
        ]
    }
    
    with pytest.raises(TaskManagementError):
        await task_manager.update_tasks(current_tasks, invalid_plan)

@pytest.mark.asyncio
async def test_update_task_status_error(task_manager):
    """Test error handling in update_task_status."""
    tasks = [
        TaskSchema(
            id="task-1",
            name="Task 1",
            description="Description 1",
            status=TaskStatus.PENDING,
            priority=TaskPriority.HIGH,
            business_impact=BusinessImpact.MEDIUM,
            estimated_duration=2.0
        )
    ]
    
    with pytest.raises(TaskManagementError):
        # Pass invalid status to trigger error
        await task_manager.update_task_status(tasks, "task-1", "invalid_status") 