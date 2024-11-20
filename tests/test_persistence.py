import pytest
from core.schemas import TaskSchema, ResourceSchema, TaskStatus, TaskPriority, BusinessImpact

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
    resource_data = ResourceSchema(
        id="test-resource",
        name="Test Resource",
        type="agent",
        status="active",
        capabilities=["python", "testing"]
    )
    
    # Save and retrieve resource
    await persistence_manager.save_resource(resource_data.id, resource_data)
    retrieved = await persistence_manager.get_resource(resource_data.id)
    
    # Verify results
    assert retrieved.id == resource_data.id
    assert retrieved.name == resource_data.name
    assert retrieved.status == resource_data.status 