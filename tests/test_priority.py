import pytest
from agents.director.priority import calculate_priority_score, calculate_task_priority
from agents.director.schemas import TaskSchema
from agents.director.enums import BusinessImpact
from core.schemas.enums import Status, Priority
def test_calculate_task_priority_high():
    """Test high priority calculation."""
    task = TaskSchema(
        id="test-task",
        name="Test Task",
        description="Test Description",
        status=Status.PENDING,
        priority=Priority.HIGH,
    )
    
    priority_score = calculate_priority_score(task)
    assert priority_score >= 8.0

def test_calculate_task_priority_medium():
    """Test medium priority calculation."""
    task = TaskSchema(
        id="test-task",
        name="Test Task",
        description="Test Description",
        status=Status.PENDING,
        priority=Priority.MEDIUM,
    )
    
    result = calculate_task_priority(task)
    assert result == Priority.MEDIUM

def test_calculate_task_priority_low():
    """Test low priority calculation."""
    task = TaskSchema(
        id="test-task",
        name="Test Task",
        description="Test Description",
        status=Status.PENDING,
        priority=Priority.LOW,
    )
    
    result = calculate_task_priority(task)
    assert result == Priority.LOW

def test_calculate_task_priority_missing_fields():
    """Test priority calculation with missing fields."""
    task = TaskSchema(
        id="test-task",
        name="Test Task",
        description="Test Description",
        status=Status.PENDING,
        priority=Priority.LOW,
    )
    
    result = calculate_task_priority(task)
    assert result == Priority.LOW