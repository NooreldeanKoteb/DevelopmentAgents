import pytest
import redis.asyncio as redis
from datetime import datetime
from agents.director.persistence import PersistenceManager
    
# Import enums
from core.schemas.enums import (
    Status,
    Priority,
    ResourceType,
    ResourceStatus,
)
from agents.director.enums import BusinessImpact

# Import schemas
from agents.director.schemas import TaskSchema   

@pytest.fixture
async def persistence_manager():
    """Provide a persistence manager instance."""
    manager = PersistenceManager(redis_url="redis://localhost:6379/0")
    try:
        yield manager
    finally:
        # Cleanup after tests
        if hasattr(manager, 'redis'):
            await manager.redis.flushdb()
            await manager.redis.aclose()

@pytest.mark.asyncio
async def test_task_crud_operations(persistence_manager):
    """Test task CRUD operations."""
    now = datetime.now()
    task = {
        "id": "test-task-1",
        "name": "Test Task",
        "description": "Test task description",
        "status": Status.PENDING,
        "priority": Priority.MEDIUM,
        "business_impact": BusinessImpact.MEDIUM,
        "estimated_duration": 1.0,
        "dependencies": [],
        "created_at": now,
        "updated_at": now,
        "metadata": {},
        "phase": None,
        "progress": 0.0,
        "assigned_to": None,
        "tags": [],
        "due_date": None,
        "subtasks": [],
        "parent_task": None,
        "requirements": {},
        "completion_criteria": [],
        "notes": ""
    }
    
    await persistence_manager.save_task(task)
    retrieved_task = await persistence_manager.get_task(task["id"])
    
    assert retrieved_task is not None
    assert retrieved_task.id == task["id"]
    assert retrieved_task.name == task["name"]
    assert retrieved_task.status == Status.PENDING
    
    # Test update
    task["status"] = Status.IN_PROGRESS
    await persistence_manager.save_task(task)
    updated_task = await persistence_manager.get_task(task["id"])
    assert updated_task.status == Status.IN_PROGRESS
    
    # Test delete
    await persistence_manager.delete_task(task["id"])
    deleted_task = await persistence_manager.get_task(task["id"])
    assert deleted_task is None

@pytest.mark.asyncio
async def test_task_indexing(persistence_manager):
    """Test task indexing."""
    now = datetime.now()
    tasks = [
        {
            "id": f"test-task-{i}",
            "name": f"Test Task {i}",
            "description": f"Test task description {i}",
            "status": Status.PENDING,
            "priority": Priority.MEDIUM,
            "business_impact": BusinessImpact.MEDIUM,
            "estimated_duration": 1.0,
            "dependencies": [],
            "created_at": now,
            "updated_at": now,
            "metadata": {},
            "phase": None,
            "progress": 0.0,
            "assigned_to": None,
            "tags": [],
            "due_date": None,
            "subtasks": [],
            "parent_task": None,
            "requirements": {},
            "completion_criteria": [],
            "notes": ""
        } for i in range(3)
    ]
    
    # Save all tasks
    for task in tasks:
        await persistence_manager.save_task(task)
    
    # Test list all tasks
    all_tasks = await persistence_manager.list_tasks()
    assert len(all_tasks) == 3
    
    # Test filtering by status
    pending_tasks = await persistence_manager.list_tasks(status=Status.PENDING)
    assert len(pending_tasks) == 3
    
    # Update one task status
    tasks[0]["status"] = Status.IN_PROGRESS
    await persistence_manager.save_task(tasks[0])
    
    # Test filtering after update
    pending_tasks = await persistence_manager.list_tasks(status=Status.PENDING)
    assert len(pending_tasks) == 2

@pytest.mark.asyncio
async def test_resource_operations(persistence_manager):
    """Test resource operations."""
    now = datetime.now()
    resource = {
        "id": "test-resource-1",
        "name": "Test Resource",
        "type": ResourceType.AGENT,
        "status": ResourceStatus.AVAILABLE,
        "capacity": 1.0,
        "current_load": 0.0,
        "capabilities": [],
        "allocated_to": None,
        "metadata": {},
        "limits": {}
    }
    
    # Test save and retrieve
    await persistence_manager.save_resource(resource)
    retrieved_resource = await persistence_manager.get_resource(resource["id"])
    
    assert retrieved_resource is not None
    assert retrieved_resource.id == resource["id"]
    assert retrieved_resource.name == resource["name"]
    assert retrieved_resource.type == resource["type"]
    assert retrieved_resource.status == resource["status"]
    
    # Test update
    resource["status"] = ResourceStatus.IN_USE
    await persistence_manager.save_resource(resource)
    updated_resource = await persistence_manager.get_resource(resource["id"])
    assert updated_resource.status == ResourceStatus.IN_USE
    
    # Test delete
    await persistence_manager.delete_resource(resource["id"])
    deleted_resource = await persistence_manager.get_resource(resource["id"])
    assert deleted_resource is None

@pytest.mark.asyncio
async def test_task_resource_relationship(persistence_manager):
    """Test task-resource relationship operations."""
    now = datetime.now()
    task = {
        "id": "test-task-1",
        "name": "Test Task",
        "description": "Test task description",
        "status": Status.PENDING,
        "priority": Priority.MEDIUM,
        "business_impact": BusinessImpact.MEDIUM,
        "estimated_duration": 1.0,
        "dependencies": [],
        "created_at": now,
        "updated_at": now,
        "metadata": {},
        "phase": None,
        "progress": 0.0,
        "assigned_to": None,
        "tags": [],
        "due_date": None,
        "subtasks": [],
        "parent_task": None,
        "requirements": {},
        "completion_criteria": [],
        "notes": ""
    }
    
    resource = {
        "id": "test-resource-1",
        "name": "Test Resource",
        "type": ResourceType.AGENT,
        "status": ResourceStatus.AVAILABLE,
        "capacity": 1.0,
        "current_load": 0.0,
        "capabilities": [],
        "allocated_to": None,
        "metadata": {},
        "limits": {}
    }
    
    # Save both
    await persistence_manager.save_task(task)
    await persistence_manager.save_resource(resource)
    
    # Assign resource to task
    await persistence_manager.assign_resource_to_task(task["id"], resource["id"])
    
    # Test resource assignment
    task_resources = await persistence_manager.get_task_resources(task["id"])
    assert len(task_resources) == 1
    assert task_resources[0].id == resource["id"]
    
    # Test task assignment
    resource_tasks = await persistence_manager.get_resource_tasks(resource["id"])
    assert len(resource_tasks) == 1
    assert resource_tasks[0].id == task["id"]
    
    # Test unassign
    await persistence_manager.unassign_resource_from_task(task["id"], resource["id"])
    task_resources = await persistence_manager.get_task_resources(task["id"])
    assert len(task_resources) == 0

@pytest.mark.asyncio
async def test_error_handling(persistence_manager):
    """Test error handling in persistence operations."""
    # Test non-existent task
    non_existent = await persistence_manager.get_task("non-existent")
    assert non_existent is None
    
    # Test invalid task data
    invalid_data = {"invalid": "data"}  # Missing required fields
    with pytest.raises(ValueError):
        await persistence_manager.save_task(invalid_data)
    
    # Test delete non-existent
    await persistence_manager.delete_task("non-existent")  # Should not raise
    
    # Test invalid resource assignment
    task_id = "non-existent-task"
    resource_id = "non-existent-resource"
    
    # Verify both task and resource don't exist
    task = await persistence_manager.get_task(task_id)
    resource = await persistence_manager.get_resource(resource_id)
    assert task is None and resource is None
    
    with pytest.raises(Exception):
        await persistence_manager.assign_resource_to_task(task_id, resource_id)