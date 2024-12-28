import pytest
from datetime import datetime, timedelta
from agents.director.priority import PriorityCalculator
from core.schemas import TaskPriority

class TestPriorityCalculator:
    @pytest.fixture
    def calculator(self):
        return PriorityCalculator()

    @pytest.mark.parametrize("minutes,expected_score", [
        (1, 100),    # Immediate
        (10, 90),    # Very urgent
        (25, 80),    # Urgent
        (45, 70),    # High priority
        (90, 50),    # Medium priority
        (150, 30),   # Lower priority
    ])
    def test_deadline_score(self, calculator, minutes, expected_score):
        assert calculator.calculate_deadline_score(minutes) == expected_score

    @pytest.mark.parametrize("impact_level,expected_score", [
        ("critical", 100),
        ("high", 80),
        ("medium", 60),
        ("low", 40),
        ("minimal", 20),
        ("unknown", 40),  # Default case
    ])
    def test_impact_score(self, calculator, impact_level, expected_score):
        task = {"business_impact": impact_level}
        assert calculator.calculate_impact_score(task) == expected_score

    def test_resource_score(self, calculator):
        blocked_task = {"resource_status": {"blocked": True}}
        limited_task = {"resource_status": {"limited": True}}
        normal_task = {"resource_status": {}}

        assert calculator.calculate_resource_score(blocked_task) == 100
        assert calculator.calculate_resource_score(limited_task) == 80
        assert calculator.calculate_resource_score(normal_task) == 40 