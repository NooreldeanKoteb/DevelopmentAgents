import pytest
import redis.asyncio as redis
from datetime import datetime
from agents.project_manager.persistence import PersistenceManager
from core.schemas import TaskSchema, ResourceSchema, TaskStatus, TaskPriority

@pytest.fixture
async def persistence_manager():
    """Provide a persistence manager instance."""
    manager = PersistenceManager(redis_url="redis://localhost:6379/0")
    yield manager
    # Cleanup after tests
    await manager.redis.flushdb()

@pytest.mark.asyncio
async def test_task_crud_operations(persistence_manager):
    """Test task CRUD operations."""
    # Create test task
    task = TaskSchema(
        id="test-task-1",
        title="Test Task",
        description="Test task description",
        status=TaskStatus.PENDING,
        priority=TaskPriority.MEDIUM,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    
    # Test save
    await persistence_manager.save_task(task)
    
    # Test retrieve
    retrieved_task = await persistence_manager.get_task(task.id)
    assert retrieved_task is not None
    assert retrieved_task.id == task.id
    assert retrieved_task.title == task.title
    assert retrieved_task.status == TaskStatus.PENDING
    
    # Test update
    task.status = TaskStatus.IN_PROGRESS
    await persistence_manager.save_task(task)
    updated_task = await persistence_manager.get_task(task.id)
    assert updated_task.status == TaskStatus.IN_PROGRESS
    
    # Test delete
    await persistence_manager.delete_task(task.id)
    deleted_task = await persistence_manager.get_task(task.id)
    assert deleted_task is None

@pytest.mark.asyncio
async def test_task_indexing(persistence_manager):
    """Test task indexing."""
    # Create multiple tasks
    tasks = [
        TaskSchema(
            id=f"test-task-{i}",
            title=f"Test Task {i}",
            description=f"Test task description {i}",
            status=TaskStatus.PENDING,
            priority=TaskPriority.MEDIUM,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        ) for i in range(3)
    ]
    
    # Save all tasks
    for task in tasks:
        await persistence_manager.save_task(task)
    
    # Test list all tasks
    all_tasks = await persistence_manager.list_tasks()
    assert len(all_tasks) == 3
    
    # Test filtering by status
    pending_tasks = await persistence_manager.list_tasks(status=TaskStatus.PENDING)
    assert len(pending_tasks) == 3
    
    # Update one task status
    tasks[0].status = TaskStatus.IN_PROGRESS
    await persistence_manager.save_task(tasks[0])
    
    # Test filtering after update
    pending_tasks = await persistence_manager.list_tasks(status=TaskStatus.PENDING)
    assert len(pending_tasks) == 2
    in_progress_tasks = await persistence_manager.list_tasks(status=TaskStatus.IN_PROGRESS)
    assert len(in_progress_tasks) == 1

@pytest.mark.asyncio
async def test_resource_operations(persistence_manager):
    """Test resource operations."""
    # Create test resource
    resource = ResourceSchema(
        id="test-resource-1",
        name="Test Resource",
        type="developer",
        capacity=1.0,
        skills=["python", "testing"],
        availability={
            "monday": {"start": "09:00", "end": "17:00"},
            "tuesday": {"start": "09:00", "end": "17:00"}
        }
    )
    
    # Test save
    await persistence_manager.save_resource(resource)
    
    # Test retrieve
    retrieved_resource = await persistence_manager.get_resource(resource.id)
    assert retrieved_resource is not None
    assert retrieved_resource.id == resource.id
    assert retrieved_resource.name == resource.name
    assert retrieved_resource.skills == resource.skills
    
    # Test update
    resource.capacity = 0.5
    await persistence_manager.save_resource(resource)
    updated_resource = await persistence_manager.get_resource(resource.id)
    assert updated_resource.capacity == 0.5
    
    # Test delete
    await persistence_manager.delete_resource(resource.id)
    deleted_resource = await persistence_manager.get_resource(resource.id)
    assert deleted_resource is None

@pytest.mark.asyncio
async def test_task_resource_relationship(persistence_manager):
    """Test task-resource relationship operations."""
    # Create test task and resource
    task = TaskSchema(
        id="test-task-1",
        title="Test Task",
        description="Test task description",
        status=TaskStatus.PENDING,
        priority=TaskPriority.MEDIUM,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    
    resource = ResourceSchema(
        id="test-resource-1",
        name="Test Resource",
        type="developer",
        capacity=1.0,
        skills=["python", "testing"]
    )
    
    # Save both
    await persistence_manager.save_task(task)
    await persistence_manager.save_resource(resource)
    
    # Assign resource to task
    await persistence_manager.assign_resource_to_task(task.id, resource.id)
    
    # Test resource assignment
    task_resources = await persistence_manager.get_task_resources(task.id)
    assert len(task_resources) == 1
    assert task_resources[0].id == resource.id
    
    # Test task assignment
    resource_tasks = await persistence_manager.get_resource_tasks(resource.id)
    assert len(resource_tasks) == 1
    assert resource_tasks[0].id == task.id
    
    # Test unassign
    await persistence_manager.unassign_resource_from_task(task.id, resource.id)
    task_resources = await persistence_manager.get_task_resources(task.id)
    assert len(task_resources) == 0

@pytest.mark.asyncio
async def test_error_handling(persistence_manager):
    """Test error handling in persistence operations."""
    # Test non-existent task
    non_existent = await persistence_manager.get_task("non-existent")
    assert non_existent is None
    
    # Test invalid task data
    with pytest.raises(Exception):
        await persistence_manager.save_task({"invalid": "data"})
    
    # Test delete non-existent
    await persistence_manager.delete_task("non-existent")  # Should not raise
    
    # Test invalid resource assignment
    with pytest.raises(Exception):
        await persistence_manager.assign_resource_to_task(
            "non-existent-task",
            "non-existent-resource"
        )