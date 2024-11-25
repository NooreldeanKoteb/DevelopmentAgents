import pytest
from datetime import datetime
from agents.project_manager.planner import ProjectPlanner
from core.schemas import TaskSchema, TaskStatus, TaskPriority, BusinessImpact

class TestProjectPlanner:
    @pytest.fixture
    def planner(self):
        return ProjectPlanner()

    @pytest.fixture
    def sample_tasks(self):
        return [
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
                estimated_duration="1.5",
                phase="phase-2",
                dependencies=["task-1"]
            )
        ]

    @pytest.mark.asyncio
    async def test_generate_timeline(self, planner, sample_tasks):
        timeline = await planner.generate_timeline(sample_tasks)
        assert "phases" in timeline
        assert "milestones" in timeline
        assert "estimated_duration" in timeline
        assert timeline["estimated_duration"] == 3.5

    @pytest.mark.asyncio
    async def test_phase_distribution(self, planner, sample_tasks):
        phases = planner._distribute_into_phases(sample_tasks)
        assert isinstance(phases, list)
        assert len(phases) > 0

    @pytest.mark.asyncio
    async def test_milestone_generation(self, planner, sample_tasks):
        milestones = planner._generate_milestones(sample_tasks)
        assert isinstance(milestones, list) 