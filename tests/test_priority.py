import pytest
from agents.director.priority import calculate_priority_score, calculate_task_priority
from agents.director.models import TaskSchema
from agents.director.enums import TaskStatus, TaskPriority, BusinessImpact

def test_calculate_task_priority_high():
    """Test high priority calculation."""
    task = TaskSchema(
        id="test-task",
        name="Test Task",
        description="Test Description",
        status=TaskStatus.PENDING,
        priority=TaskPriority.HIGH,
    )
    
    priority_score = calculate_priority_score(task)
    assert priority_score >= 8.0

def test_calculate_task_priority_medium():
    """Test medium priority calculation."""
    task = TaskSchema(
        id="test-task",
        name="Test Task",
        description="Test Description",
        status=TaskStatus.PENDING,
        priority=TaskPriority.MEDIUM,
    )
    
    result = calculate_task_priority(task)
    assert result == TaskPriority.MEDIUM

def test_calculate_task_priority_low():
    """Test low priority calculation."""
    task = TaskSchema(
        id="test-task",
        name="Test Task",
        description="Test Description",
        status=TaskStatus.PENDING,
        priority=TaskPriority.LOW,
    )
    
    result = calculate_task_priority(task)
    assert result == TaskPriority.LOW

def test_calculate_task_priority_missing_fields():
    """Test priority calculation with missing fields."""
    task = TaskSchema(
        id="test-task",
        name="Test Task",
        description="Test Description",
        status=TaskStatus.PENDING,
        priority=TaskPriority.LOW,
    )
    
    result = calculate_task_priority(task)
    assert result == TaskPriority.LOW