import pytest
from core.schemas import BusinessImpact
from agents.project_manager.priority import calculate_task_priority

def test_calculate_task_priority_high():
    """Test high priority calculation."""
    task = {
        "estimated_duration": "5.0",
        "dependencies": ["task-1", "task-2", "task-3"],
        "business_impact": BusinessImpact.HIGH,
        "status": "blocked"
    }
    assert calculate_task_priority(task) == "high"

def test_calculate_task_priority_medium():
    """Test medium priority calculation."""
    task = {
        "estimated_duration": 3.0,  # Medium duration (+2)
        "dependencies": ["task-1"],  # Few dependencies (+2)
        "business_impact": "medium",  # Medium impact (+2)
        "status": "pending"  # Pending status (+0)
    }
    assert calculate_task_priority(task) == "medium"  # Score: 6

def test_calculate_task_priority_low():
    """Test low priority calculation."""
    task = {
        "estimated_duration": 1.0,  # Low duration (+1)
        "dependencies": [],  # No dependencies (+0)
        "business_impact": "low",  # Low impact (+1)
        "status": "pending"  # Pending status (+0)
    }
    assert calculate_task_priority(task) == "low"  # Score: 2

def test_calculate_task_priority_missing_fields():
    """Test priority calculation with missing fields."""
    task = {
        "status": "pending"
    }
    # Should use default values and return low priority
    assert calculate_task_priority(task) == "low"