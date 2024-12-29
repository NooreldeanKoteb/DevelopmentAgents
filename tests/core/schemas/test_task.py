import pytest
from pydantic import ValidationError
from agents.director.schemas import TaskSchema
from agents.director.enums import BusinessImpact
from core.schemas.enums import Status, Priority

def test_task_schema():
    """Test TaskSchema validation and defaults."""
    task = TaskSchema(
        id="test-task",
        name="Test Task",
        description="Test description",
        status=Status.PENDING,
        priority=Priority.MEDIUM,
        phase="testing"
    )
    assert task.id == "test-task"
    assert task.status == Status.PENDING
    assert task.business_impact == BusinessImpact.LOW

def test_task_status_transitions():
    """Test task status transitions."""
    task = TaskSchema(
        id="test-task",
        name="Test Task",
        description="Test description",
        priority=Priority.MEDIUM,
    )
    
    # Test valid transitions
    task.status = Status.IN_PROGRESS
    assert task.status == Status.IN_PROGRESS
    
    task.status = Status.COMPLETED
    assert task.status == Status.COMPLETED