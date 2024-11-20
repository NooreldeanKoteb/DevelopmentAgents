import pytest
from core.schemas import TaskSchema, TaskStatus, TaskPriority, BusinessImpact, ResourceSchema
from agents.project_manager.enums import TaskStatus, Priority, BusinessImpact
from datetime import datetime
from agents.project_manager.models import ResourceData
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
            estimated_duration="1.5",
            phase="phase-1"
        )
        
        result = await task_manager.create_task(task.model_dump())
        assert result.priority == Priority.HIGH
        assert result.status == TaskStatus.PENDING
        
        tasks = await task_manager.get_tasks_by_priority(Priority.HIGH)
        assert len(tasks) > 0

    @pytest.mark.asyncio
    async def test_resource_allocation_workflow(self, resource_manager, persistence_manager):
        resource_data = ResourceData(
            id="resource-1",
            name="Test Resource",
            type="agent",
            status="active",
            capabilities=["python", "testing"],
            current_load=0.0,
            capacity=1.0,
            performance_score=0.8
        )
        
        resource_manager.persistence = persistence_manager
        result = await resource_manager.allocate_resource(resource_data.model_dump())
        
        assert result["action_type"] == "resource_allocation"
        assert result["status"] == "success"
        assert result["resource_id"] == "resource-1"
  