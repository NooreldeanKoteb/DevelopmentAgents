import pytest
from prometheus_client import REGISTRY
from agents.director.monitoring import (
    ProjectMetrics,
    TaskMetrics,
    ResourceMetrics,
    setup_monitoring
)
from core.schemas import TaskSchema, ResourceSchema
from core.schemas.enums import (
    TaskStatus,
    TaskPriority,
    BusinessImpact,
    ResourceType,
    ResourceStatus
)

@pytest.fixture(autouse=True)
def clear_prometheus_registry():
    """Clear Prometheus registry before each test."""
    for collector in list(REGISTRY._collector_to_names.keys()):
        REGISTRY.unregister(collector)
    yield

@pytest.fixture
def project_metrics():
    """Create ProjectMetrics instance."""
    return ProjectMetrics()

@pytest.fixture
def task_metrics():
    """Create TaskMetrics instance."""
    return TaskMetrics()

@pytest.fixture
def resource_metrics():
    """Create ResourceMetrics instance."""
    return ResourceMetrics()

@pytest.mark.asyncio
async def test_task_metrics_tracking(task_metrics):
    """Test task metrics tracking."""
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
    
    # Test task creation
    task_metrics.track_task_creation(task)
    assert REGISTRY.get_sample_value('pm_task_count_total') == 1
    
    # Test status update
    task_metrics.track_task_status_update(task, TaskStatus.IN_PROGRESS)
    assert REGISTRY.get_sample_value('pm_task_status_changes_total', {'status': 'IN_PROGRESS'}) == 1
    
    # Test task completion
    task_metrics.track_task_completion(task, 2.5)  # 2.5 hours duration
    assert REGISTRY.get_sample_value('pm_task_completion_time_seconds_sum') > 0

@pytest.mark.asyncio
async def test_resource_metrics_tracking(resource_metrics):
    """Test resource metrics tracking."""
    resource = ResourceSchema(
        id="test-resource",
        name="Test Resource",
        type=ResourceType.AGENT,
        status=ResourceStatus.AVAILABLE,
        capacity=1.0,
        current_usage=0.0
    )
    
    # Test resource allocation
    resource_metrics.track_resource_allocation(resource)
    assert REGISTRY.get_sample_value('pm_resource_allocation_total') == 1
    
    # Test resource utilization
    resource_metrics.track_resource_utilization(resource, 0.75)  # 75% utilization
    assert REGISTRY.get_sample_value('pm_resource_utilization_ratio', {'resource_id': 'test-resource'}) == 0.75

@pytest.mark.asyncio
async def test_project_metrics_tracking(project_metrics):
    """Test project metrics tracking."""
    # Test project creation
    project_metrics.track_project_creation("test-project")
    assert REGISTRY.get_sample_value('pm_project_count_total') == 1
    
    # Test project completion
    project_metrics.track_project_completion("test-project", 24.0)  # 24 hours duration
    assert REGISTRY.get_sample_value('pm_project_completion_time_hours_sum') > 0

def test_setup_monitoring():
    """Test monitoring setup."""
    metrics = setup_monitoring()
    assert isinstance(metrics["project_metrics"], ProjectMetrics)
    assert isinstance(metrics["task_metrics"], TaskMetrics)
    assert isinstance(metrics["resource_metrics"], ResourceMetrics) 