from prometheus_client import Counter, Gauge, Histogram, Summary, REGISTRY
from typing import Dict, Any
from datetime import datetime
import logging
from contextlib import contextmanager
import time
from core.schemas.enums import Status
__all__ = ['ProjectMetrics', 'TaskMetrics', 'ResourceMetrics', 'setup_monitoring']

class ProjectMetrics:
    """Metrics for project-related operations."""
    def __init__(self):
        self.project_count = Counter(
            'pm_project_count_total',
            'Total number of projects created'
        )
        self.project_completion_time = Histogram(
            'pm_project_completion_time_hours',
            'Time taken to complete projects'
        )

    def track_project_creation(self, project_id: str):
        """Track project creation."""
        self.project_count.inc()

    def track_project_completion(self, project_id: str, duration: float):
        """Track project completion time."""
        self.project_completion_time.observe(duration)

class TaskMetrics:
    """Metrics for task-related operations."""
    def __init__(self):
        self.task_count = Counter(
            'pm_task_count_total',
            'Total number of tasks created'
        )
        self.task_status_changes = Counter(
            'pm_task_status_changes_total',
            'Number of task status changes',
            ['status']
        )
        self.task_completion_time = Histogram(
            'pm_task_completion_time_seconds',
            'Time taken to complete tasks'
        )

    def track_task_creation(self, task):
        """Track task creation."""
        self.task_count.inc()

    def track_task_status_update(self, task, new_status):
        """Track task status updates."""
        if isinstance(new_status, Status):
            status_str = new_status.name
        else:
            status_str = str(new_status).replace('Status.', '')
        self.task_status_changes.labels(status=status_str).inc()

    def track_task_completion(self, task, duration):
        """Track task completion time."""
        self.task_completion_time.observe(duration)

class ResourceMetrics:
    """Metrics for resource-related operations."""
    def __init__(self):
        self.resource_allocation = Counter(
            'pm_resource_allocation_total',
            'Total number of resource allocations'
        )
        self.resource_utilization = Gauge(
            'pm_resource_utilization_ratio',
            'Current resource utilization ratio',
            ['resource_id']
        )

    def track_resource_allocation(self, resource):
        """Track resource allocation."""
        self.resource_allocation.inc()

    def track_resource_utilization(self, resource, utilization):
        """Track resource utilization."""
        self.resource_utilization.labels(resource_id=resource.id).set(utilization)

def setup_monitoring() -> Dict[str, Any]:
    """Set up monitoring metrics."""
    return {
        "project_metrics": ProjectMetrics(),
        "task_metrics": TaskMetrics(),
        "resource_metrics": ResourceMetrics()
    } 