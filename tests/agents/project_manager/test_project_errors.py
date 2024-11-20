import pytest
from agents.project_manager.errors import (
    ProjectError,
    TaskError,
    ResourceError,
    PlanningError,
    TaskNotFoundError,
    ResourceNotFoundError,
    DependencyError,
    ResourceAllocationError,
    InvalidTaskStateError,
    InvalidPriorityError
)

def test_project_error():
    """Test project error."""
    error = ProjectError("Test error")
    assert isinstance(error, ProjectError)
    assert str(error) == "Test error"

def test_task_error():
    """Test task error."""
    error = TaskError("Task error")
    assert isinstance(error, ProjectError)
    assert str(error) == "Task error"

def test_resource_error():
    """Test resource error."""
    error = ResourceError("Resource error")
    assert isinstance(error, ProjectError)
    assert str(error) == "Resource error"

def test_planning_error():
    """Test planning error."""
    error = PlanningError("Planning error")
    assert isinstance(error, ProjectError)
    assert str(error) == "Planning error"

def test_specific_errors():
    """Test specific error types."""
    errors = [
        TaskNotFoundError("Task not found"),
        ResourceNotFoundError("Resource not found"),
        DependencyError("Dependency error"),
        ResourceAllocationError("Resource allocation error"),
        InvalidTaskStateError("Invalid task state"),
        InvalidPriorityError("Invalid priority")
    ]
    
    for error in errors:
        assert isinstance(error, ProjectError)
        assert str(error) is not None 