from typing import Dict, Any
from datetime import datetime
import logging
from prometheus_client import Counter, Gauge, Histogram, CollectorRegistry
from contextlib import contextmanager
import time

# Create a singleton registry
REGISTRY = CollectorRegistry()

class MetricsManager:
    _instance = None
    _metrics = {}
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if not self._initialized:
            self._init_metrics()
            self._initialized = True
    
    def _get_or_create_metric(self, name: str, metric_type, *args, **kwargs):
        """Get existing metric or create new one."""
        if name not in self._metrics:
            self._metrics[name] = metric_type(name, *args, registry=REGISTRY, **kwargs)
        return self._metrics[name]
    
    def _init_metrics(self):
        """Initialize all metrics."""
        # Task metrics
        self.task_created = Counter(
            'tasks_created_total',
            'Total number of tasks created',
            registry=REGISTRY
        )
        
        self.task_completed = Counter(
            'tasks_completed_total',
            'Total number of tasks completed',
            registry=REGISTRY
        )
        
        self.task_status = Gauge(
            'task_status',
            'Current task status',
            ['task_id', 'status'],
            registry=REGISTRY
        )
        
        # Resource metrics
        self.resource_allocations = self._get_or_create_metric(
            'resource_allocations_total',
            Counter,
            'Number of resource allocations'
        )
        
        self.resource_utilization = self._get_or_create_metric(
            'resource_utilization_gauge',
            Gauge,
            'Current resource utilization percentage',
            ['resource_id']
        )
        
        self.resource_load = Gauge(
            'resource_load',
            'Current resource load',
            ['resource_id'],
            registry=REGISTRY
        )
        
        # Project metrics
        self.project_progress = Gauge(
            'project_progress',
            'Current project progress percentage',
            ['project_id'],
            registry=REGISTRY
        )
        
        # Performance metrics
        self.operation_duration = Gauge(
            'operation_duration_seconds',
            'Duration of operations',
            ['operation_type'],
            registry=REGISTRY
        )
        
        self.error_count = Counter(
            'errors_total',
            'Total number of errors',
            ['error_type'],
            registry=REGISTRY
        )
    
    def increment_task_created(self):
        """Increment the task created counter."""
        self.task_created.inc()
    
    def increment_task_completed(self):
        """Increment the task completed counter."""
        self.task_completed.inc()
    
    def set_task_status(self, task_id: str, status: str):
        """Update task status gauge."""
        self.task_status.labels(task_id=task_id, status=status).set(1)
    
    def increment_resource_allocation(self):
        """Increment the resource allocation counter."""
        self.resource_allocations.inc()
    
    def set_resource_utilization(self, resource_id: str, value: float):
        """Update resource utilization gauge."""
        self.resource_utilization.labels(resource_id=resource_id).set(value)
    
    def set_resource_load(self, resource_id: str, value: float):
        """Update resource load gauge."""
        self.resource_load.labels(resource_id=resource_id).set(value)
    
    def set_project_progress(self, project_id: str, value: float):
        """Update project progress gauge."""
        self.project_progress.labels(project_id=project_id).set(value)
    
    def record_operation_duration(self, operation_type: str, duration: float):
        """Record operation duration."""
        self.operation_duration.labels(operation_type=operation_type).set(duration)
    
    def increment_error(self, error_type: str):
        """Increment error counter for specific error type."""
        self.error_count.labels(error_type=error_type).inc()

# Create singleton instance
metrics_manager = MetricsManager()

class ProjectMetrics:
    def __init__(self) -> None:
        # Counters
        self.task_counter = Counter(
            'project_tasks_total',
            'Total number of tasks',
            ['status']
        )
        self.error_counter = Counter(
            'project_errors_total',
            'Total number of errors',
            ['type']
        )
        
        # Gauges
        self.active_tasks = Gauge(
            'project_active_tasks',
            'Number of currently active tasks'
        )
        self.resource_utilization = Gauge(
            'project_resource_utilization',
            'Resource utilization percentage',
            ['resource_type']
        )
        
        # Histograms
        self.task_duration = Histogram(
            'task_duration_seconds',
            'Task completion time in seconds',
            buckets=[60, 300, 900, 3600, 7200, 14400]
        )
        
        # Setup logging
        self.logger = logging.getLogger("project_manager")
        self.logger.setLevel(logging.INFO)
        
        # Add handlers if not already present
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)

    @contextmanager
    def task_timer(self, task_id: str):
        """Context manager to time task execution."""
        start_time = time.time()
        try:
            yield
        finally:
            duration = time.time() - start_time
            self.task_duration.observe(duration)
            self.logger.info(f"Task {task_id} completed in {duration:.2f} seconds")

    def log_event(self, event_type: str, details: Dict[str, Any]) -> None:
        """Log project events with structured data."""
        self.logger.info({
            "event_type": event_type,
            "timestamp": datetime.utcnow().isoformat(),
            "details": details
        })

    def record_error(self, error_type: str, error_details: Dict[str, Any]) -> None:
        """Record and log errors."""
        self.error_counter.labels(type=error_type).inc()
        self.logger.error({
            "error_type": error_type,
            "timestamp": datetime.utcnow().isoformat(),
            "details": error_details
        })

    def update_task_status(self, status: str) -> None:
        """Update task status metrics."""
        self.task_counter.labels(status=status).inc()
        if status == "active":
            self.active_tasks.inc()
        elif status in ["completed", "failed"]:
            self.active_tasks.dec()

    def update_resource_utilization(self, resource_type: str, utilization: float) -> None:
        """Update resource utilization metrics."""
        self.resource_utilization.labels(resource_type=resource_type).set(utilization) 