import pytest
from agents.director.errors import (
    DirectorError,
    ProjectError,
    TaskError,
    ResourceError,
    PlanningError,
    TaskManagementError,
    ResourceManagementError,
    ProjectStateError,
    DependencyError,
    ResourceAllocationError,
    ProjectValidationError,
    TaskSchedulingError,
    AgentAssignmentError,
    ProjectTimelineError,
    ResourceConflictError,
    ProjectNotFoundError,
    TaskNotFoundError,
    ResourceNotFoundError
)

def test_director_error():
    """Test base Director error."""
    error = DirectorError("Test error")
    assert isinstance(error, DirectorError)
    assert str(error) == "Test error"

def test_project_error():
    """Test project error."""
    error = ProjectError("Test error")
    assert isinstance(error, DirectorError)
    assert str(error) == "Test error"

def test_resource_error():
    """Test resource error."""
    error = ResourceError("Resource error")
    assert isinstance(error, ProjectError)
    assert str(error) == "Resource error"

def test_resource_not_found_error():
    """Test resource not found error."""
    error = ResourceNotFoundError("resource-1", "project-1")
    assert isinstance(error, ResourceError)
    assert error.resource_id == "resource-1"
    assert error.project_id == "project-1"
    assert "Resource 'resource-1' not found in project 'project-1'" in str(error)

def test_resource_conflict_error():
    """Test resource conflict error."""
    conflicting_tasks = ["task-1", "task-2"]
    error = ResourceConflictError("resource-1", conflicting_tasks)
    assert isinstance(error, ResourceError)
    assert error.resource_id == "resource-1"
    assert error.conflicting_tasks == conflicting_tasks

def test_task_not_found_error():
    """Test task not found error."""
    error = TaskNotFoundError("task-1", "project-1")
    assert isinstance(error, TaskError)
    assert error.task_id == "task-1"
    assert error.project_id == "project-1"
    assert "Task 'task-1' not found in project 'project-1'" in str(error)

def test_project_state_error():
    """Test project state error."""
    error = ProjectStateError("in_progress", "completed")
    assert isinstance(error, ProjectError)
    assert error.current_state == "in_progress"
    assert error.attempted_transition == "completed"

def test_dependency_error():
    """Test dependency error."""
    error = DependencyError("task-1", "task-2", "Circular dependency")
    assert isinstance(error, TaskError)
    assert error.task_id == "task-1"
    assert error.dependency_id == "task-2"

def test_resource_allocation_error():
    """Test resource allocation error."""
    required = {"cpu": 2, "memory": "4GB"}
    available = {"cpu": 1, "memory": "2GB"}
    error = ResourceAllocationError("task-1", required, available)
    assert isinstance(error, ResourceError)
    assert error.task_id == "task-1"
    assert error.required_resources == required
    assert error.available_resources == available