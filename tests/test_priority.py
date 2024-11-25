import pytest
from core.schemas import TaskSchema
from core.schemas.enums import TaskStatus, TaskPriority, BusinessImpact
from agents.project_manager.priority import calculate_priority_score, calculate_task_priority

def test_calculate_task_priority_high():
    """Test high priority calculation."""
    task = TaskSchema(
        id="test-task",
        name="Test Task",
        description="Test Description",
        status=TaskStatus.PENDING,
        priority=TaskPriority.HIGH,
        business_impact=BusinessImpact.HIGH,
        estimated_duration=2.0,
        dependencies=[]
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
        business_impact=BusinessImpact.MEDIUM,
        estimated_duration=3.0,
        dependencies=["task-1"]
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
        business_impact=BusinessImpact.LOW,
        estimated_duration=1.0,
        dependencies=[]
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
        business_impact=BusinessImpact.LOW,
        estimated_duration=1.0,
        dependencies=[]
    )
    
    result = calculate_task_priority(task)
    assert result == TaskPriority.LOW