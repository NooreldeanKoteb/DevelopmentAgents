import pytest
from datetime import datetime
from agents.director.planner import ProjectPlanner
from unittest.mock import MagicMock, AsyncMock
from agents.director.enums import BusinessImpact
from agents.director.schemas import TaskSchema
from core.schemas.enums import Status, Priority
class TestProjectPlanner:
    @pytest.fixture
    def mock_director(self):
        """Create a mock director for testing."""
        mock_agent = MagicMock()
        mock_agent.openai = MagicMock()
        mock_agent.openai.get_completion = AsyncMock()
        return mock_agent

    @pytest.fixture
    def planner(self, mock_director):
        """Create a project planner instance for testing."""
        return ProjectPlanner(agent=mock_director)

    @pytest.fixture
    def sample_tasks(self):
        return [
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
                phase="phase-2",
            )
        ]

    @pytest.mark.asyncio
    async def test_generate_timeline(self, planner, sample_tasks):
        timeline = await planner.generate_timeline(sample_tasks)
        assert isinstance(timeline, dict)
        assert "phases" in timeline
        assert "milestones" in timeline
        assert "estimated_duration" in timeline

    @pytest.mark.asyncio
    async def test_phase_distribution(self, planner, sample_tasks):
        phases = planner._distribute_into_phases(sample_tasks)
        assert isinstance(phases, list)
        assert len(phases) > 0

    @pytest.mark.asyncio
    async def test_milestone_generation(self, planner, sample_tasks):
        milestones = planner._generate_milestones(sample_tasks)
        assert isinstance(milestones, list) 