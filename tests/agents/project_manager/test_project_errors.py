import pytest
from agents.project_manager.errors import (
    ProjectError,
    TaskError,
    ResourceError,
    PlanningError
)

def test_project_error():
    """Test project error."""
    error = ProjectError("Test error")
    assert str(error) == "Test error"

def test_task_error():
    """Test task error."""
    error = TaskError("Task error")
    assert isinstance(error, ProjectError)
    assert str(error) == "Task error" 