import pytest
from core.schemas import TaskSchema, TaskStatus, TaskPriority, BusinessImpact

class TestEndToEnd:
    @pytest.mark.asyncio
    async def test_complete_project_lifecycle(self, project_manager, planner):
        # Create project plan
        tasks = [
            TaskSchema(
                id="task-1",
                name="Task 1",
                description="Task 1 description",
                status=TaskStatus.PENDING,
                priority=TaskPriority.HIGH,
                business_impact=BusinessImpact.HIGH,
                estimated_duration="2.0",
                phase="phase-1",
                dependencies=[]
            ),
            TaskSchema(
                id="task-2",
                name="Task 2",
                description="Task 2 description",
                status=TaskStatus.PENDING,
                priority=TaskPriority.MEDIUM,
                business_impact=BusinessImpact.MEDIUM,
                estimated_duration="3.0",
                phase="phase-1",
                dependencies=["task-1"]
            )
        ]
        
        project_data = {
            "name": "Test Project",
            "tasks": [task.model_dump() for task in tasks]
        }
        
        plan = await planner.create_project_plan(project_data)
        assert "critical_path" in plan
        assert len(plan["tasks"]) == 2 