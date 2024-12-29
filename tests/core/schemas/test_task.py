import pytest
from pydantic import ValidationError
from agents.director.models import TaskSchema
from agents.director.enums import TaskStatus, TaskPriority, BusinessImpact

def test_task_schema():
    """Test TaskSchema validation and defaults."""
    task = TaskSchema(
        id="test-task",
        name="Test Task",
        description="Test description",
        status=TaskStatus.PENDING,
        priority=TaskPriority.MEDIUM,
        phase="testing"
    )
    assert task.id == "test-task"
    assert task.status == TaskStatus.PENDING
    assert task.business_impact == BusinessImpact.LOW

def test_task_status_transitions():
    """Test task status transitions."""
    task = TaskSchema(
        id="test-task",
        name="Test Task",
        description="Test description",
        priority=TaskPriority.MEDIUM,
    )
    
    # Test valid transitions
    task.status = TaskStatus.IN_PROGRESS
    assert task.status == TaskStatus.IN_PROGRESS
    
    task.status = TaskStatus.COMPLETED
    assert task.status == TaskStatus.COMPLETED