import pytest
from core.schemas import TaskSchema, ResourceSchema, TaskStatus, TaskPriority, BusinessImpact, ResourceType, ResourceStatus

@pytest.mark.asyncio
async def test_save_and_get_task(persistence_manager):
    """Test saving and retrieving a task."""
    task_data = TaskSchema(
        id="test-task",
        name="Test Task",
        description="Test Description",
        status=TaskStatus.PENDING,
        priority=TaskPriority.HIGH,
        business_impact=BusinessImpact.MEDIUM,
        estimated_duration=2.0,
        dependencies=[]
    )
    
    # Save and retrieve task
    await persistence_manager.save_task(task_data.id, task_data)
    retrieved = await persistence_manager.get_task(task_data.id)
    
    # Verify results
    assert retrieved.id == task_data.id
    assert retrieved.name == task_data.name
    assert retrieved.status == task_data.status
    assert retrieved.priority == task_data.priority
    assert retrieved.business_impact == task_data.business_impact

@pytest.mark.asyncio
async def test_save_and_get_resource(persistence_manager):
    """Test saving and retrieving a resource."""
    resource = {
        "id": "test-resource",
        "name": "Test Resource",
        "type": ResourceType.AGENT,
        "status": ResourceStatus.AVAILABLE,
        "capacity": 1.0,
        "current_usage": 0.0,
        "limits": {},
        "metadata": {}
    }
    
    # Save and retrieve resource
    await persistence_manager.save_resource(resource["id"], resource)
    retrieved = await persistence_manager.get_resource(resource["id"])
    
    # Verify results
    assert retrieved.id == resource["id"]
    assert retrieved.name == resource["name"]
    assert retrieved.type == resource["type"]
    assert retrieved.status == resource["status"] 