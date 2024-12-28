import pytest
from core.schemas.enums import (
    TaskStatus,
    TaskPriority,
    BusinessImpact,
    ResourceType,
    ResourceStatus
)
from core.schemas import TaskSchema, ResourceSchema
from datetime import datetime
from prometheus_client import REGISTRY  
import json
import asyncio

class TestProjectWorkflow:
    @pytest.fixture(autouse=True)
    def setup_method(self):
        """Reset metrics between tests."""
        for collector in list(REGISTRY._collector_to_names.keys()):
            REGISTRY.unregister(collector)
        yield

    @pytest.mark.asyncio
    async def test_task_creation_workflow(self, task_manager):
        task = TaskSchema(
            id="test-task",
            name="Test Task",
            description="Test task",
            status=TaskStatus.PENDING,
            priority=TaskPriority.HIGH,
            business_impact=BusinessImpact.HIGH,
            estimated_duration=1.5,
            phase="phase-1"
        )
        
        result = await task_manager.create_task(task.model_dump())
        assert result.priority == TaskPriority.HIGH
        assert result.status == TaskStatus.PENDING
        
        tasks = await task_manager.get_tasks_by_priority(TaskPriority.HIGH)
        assert len(tasks) > 0

    @pytest.mark.asyncio
    async def test_resource_allocation_workflow(self, resource_manager, persistence_manager):
        resource_data = ResourceSchema(
            id="test-resource",
            name="Test Resource",
            type=ResourceType.AGENT,
            status=ResourceStatus.AVAILABLE,
            capacity=1.0,
            current_usage=0.0,
            limits={},
            metadata={},
            capabilities=["python", "testing"]
        )
        
        resource_manager.persistence = persistence_manager
        result = await resource_manager.allocate_resource(resource_data.id, resource_data)
        
        assert result["action_type"] == "resource_allocation"
        assert result["status"] == "success"
        assert result["resource_id"] == "test-resource"
  