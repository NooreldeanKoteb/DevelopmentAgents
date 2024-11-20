import pytest
from agents.project_manager.errors import *

def test_planning_error():
    """Test PlanningError."""
    with pytest.raises(PlanningError) as exc_info:
        raise PlanningError("Failed to create plan")
    assert str(exc_info.value) == "Failed to create plan"
    assert isinstance(exc_info.value, ProjectManagerError)

def test_project_state_error():
    """Test ProjectStateError."""
    with pytest.raises(ProjectStateError) as exc_info:
        raise ProjectStateError("PLANNING", "COMPLETED")
    assert "Invalid state transition" in str(exc_info.value)
    assert exc_info.value.current_state == "PLANNING"
    assert exc_info.value.attempted_transition == "COMPLETED"

def test_dependency_error():
    """Test DependencyError."""
    with pytest.raises(DependencyError) as exc_info:
        raise DependencyError("task-1", "task-2", "Circular dependency detected")
    assert "Circular dependency detected" in str(exc_info.value)
    assert exc_info.value.task_id == "task-1"
    assert exc_info.value.dependency_id == "task-2"

def test_resource_allocation_error():
    """Test ResourceAllocationError."""
    required = {"cpu": 2, "memory": 4}
    available = {"cpu": 1, "memory": 2}
    
    with pytest.raises(ResourceAllocationError) as exc_info:
        raise ResourceAllocationError("task-1", required, available)
    assert "Failed to allocate resources" in str(exc_info.value)
    assert exc_info.value.required_resources == required
    assert exc_info.value.available_resources == available

def test_project_validation_error():
    """Test ProjectValidationError."""
    errors = ["Missing deadline", "Invalid dependencies"]
    
    with pytest.raises(ProjectValidationError) as exc_info:
        raise ProjectValidationError("project-1", errors)
    assert "validation failed" in str(exc_info.value)
    assert exc_info.value.validation_errors == errors

def test_task_scheduling_error():
    """Test TaskSchedulingError."""
    with pytest.raises(TaskSchedulingError) as exc_info:
        raise TaskSchedulingError("task-1", "Resource conflict")
    assert "Failed to schedule task" in str(exc_info.value)
    assert exc_info.value.task_id == "task-1"

def test_agent_assignment_error():
    """Test AgentAssignmentError."""
    with pytest.raises(AgentAssignmentError) as exc_info:
        raise AgentAssignmentError("task-1", "agent-1", "Agent unavailable")
    assert "Failed to assign agent" in str(exc_info.value)
    assert exc_info.value.task_id == "task-1"
    assert exc_info.value.agent_id == "agent-1"

def test_project_timeline_error():
    """Test ProjectTimelineError."""
    with pytest.raises(ProjectTimelineError) as exc_info:
        raise ProjectTimelineError("project-1", "Deadline exceeded")
    assert "timeline error" in str(exc_info.value)
    assert exc_info.value.project_id == "project-1"

def test_resource_conflict_error():
    """Test ResourceConflictError."""
    conflicting_tasks = ["task-1", "task-2"]
    
    with pytest.raises(ResourceConflictError) as exc_info:
        raise ResourceConflictError("resource-1", conflicting_tasks)
    assert "Resource conflict" in str(exc_info.value)
    assert exc_info.value.resource_id == "resource-1"
    assert exc_info.value.conflicting_tasks == conflicting_tasks

def test_project_not_found_error():
    """Test ProjectNotFoundError."""
    with pytest.raises(ProjectNotFoundError) as exc_info:
        raise ProjectNotFoundError("project-1")
    assert "Project 'project-1' not found" in str(exc_info.value)
    assert exc_info.value.project_id == "project-1"

def test_task_not_found_error():
    """Test TaskNotFoundError."""
    with pytest.raises(TaskNotFoundError) as exc_info:
        raise TaskNotFoundError("task-1", "project-1")
    assert "Task 'task-1' not found in project 'project-1'" in str(exc_info.value)
    assert exc_info.value.task_id == "task-1"
    assert exc_info.value.project_id == "project-1" 