import pytest
from agents.director.schemas import TaskSchema
from agents.director.enums import BusinessImpact
from agents.director.resource_manager import ResourceManager
from core.schemas.enums import Status, Priority
class TestEndToEnd:
    @pytest.mark.asyncio
    async def test_complete_project_lifecycle(self, persistence_manager):
        """Test complete project lifecycle."""
        resource_manager = ResourceManager(persistence_manager=persistence_manager)
        # Create project plan
        tasks = [
            TaskSchema(
                id="task-1",
                name="Task 1",
                description="Task 1 description",
                status=Status.PENDING,
                priority=Priority.HIGH,
                phase="phase-1"
            ),
            TaskSchema(
                id="task-2",
                name="Task 2",
                description="Task 2 description",
                status=Status.PENDING,
                priority=Priority.MEDIUM,
                phase="phase-1"
            )
        ]
        
        project_data = {
            "name": "Test Project",
            "tasks": [task.model_dump() for task in tasks]
        }
        
        plan = await resource_manager.create_project_plan(project_data)
        assert "critical_path" in plan
        assert len(plan["tasks"]) == 2 