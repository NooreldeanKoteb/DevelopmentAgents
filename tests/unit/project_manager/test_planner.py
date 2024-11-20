import pytest
from datetime import datetime
from agents.project_manager.planner import ProjectPlanner

class TestProjectPlanner:
    @pytest.fixture
    def planner(self):
        return ProjectPlanner()

    @pytest.fixture
    def sample_tasks(self):
        return [
            {
                "id": "task-1",
                "name": "Task 1",
                "estimated_duration": 2.0,
                "dependencies": []
            },
            {
                "id": "task-2",
                "name": "Task 2",
                "estimated_duration": 3.0,
                "dependencies": ["task-1"]
            },
            {
                "id": "task-3",
                "name": "Task 3",
                "estimated_duration": 1.0,
                "dependencies": ["task-2"]
            }
        ]

    @pytest.mark.asyncio
    async def test_generate_timeline(self, planner, sample_tasks):
        timeline = await planner.generate_timeline(sample_tasks)
        
        assert "start_date" in timeline
        assert "end_date" in timeline
        assert "critical_path" in timeline
        assert "phases" in timeline
        assert "milestones" in timeline
        
        # Verify critical path
        critical_path = timeline["critical_path"]
        assert len(critical_path) == 3
        assert critical_path[0]["id"] == "task-1"
        assert critical_path[-1]["id"] == "task-3"

    def test_phase_distribution(self, planner, sample_tasks):
        phases = planner._distribute_into_phases(sample_tasks)
        assert len(phases) > 0
        assert all(isinstance(phase, list) for phase in phases)

    def test_milestone_generation(self, planner, sample_tasks):
        phases = planner._distribute_into_phases(sample_tasks)
        milestones = planner._generate_milestones(phases)
        
        assert len(milestones) == len(phases)
        assert all("name" in m and "date" in m for m in milestones) 