from typing import Dict, Any
from datetime import datetime
import logging
from prometheus_client import Counter, Gauge, Histogram
from contextlib import contextmanager
import time

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