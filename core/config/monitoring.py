import functools
import time
from typing import Callable, Any
from prometheus_client import Counter, Histogram, REGISTRY
from functools import wraps
from typing import Dict, Any

class MetricsRegistry:
    """Singleton metrics registry."""
    _instance = None
    _metrics: Dict[str, Any] = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        # Initialize metrics if they don't exist or have been unregistered
        if not self._metrics or not all(m.describe()[0].name in REGISTRY._names_to_collectors 
                                      for m in self._metrics.values()):
            # Unregister any existing metrics first
            for name in ['agent_requests_total', 'agent_errors_total', 'agent_operation_duration_seconds']:
                try:
                    REGISTRY.unregister(REGISTRY._names_to_collectors[name])
                except KeyError:
                    pass

            # Create new metrics
            self._metrics = {
                'requests': Counter(
                    'agent_requests_total',
                    'Total requests by agent type and operation',
                    ['agent_type', 'operation']
                ),
                'errors': Counter(
                    'agent_errors_total',
                    'Total errors by agent type and error type',
                    ['agent_type', 'error_type']
                ),
                'duration': Histogram(
                    'agent_operation_duration_seconds',
                    'Operation duration in seconds',
                    ['agent_type', 'operation']
                )
            }

def monitor_operation(agent_type: str, operation: str):
    """Decorator to monitor agent operations."""
    registry = MetricsRegistry()
    
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                registry._metrics['requests'].labels(
                    agent_type=agent_type,
                    operation=operation
                ).inc()
                
                result = await func(*args, **kwargs)
                
                registry._metrics['duration'].labels(
                    agent_type=agent_type,
                    operation=operation
                ).observe(time.time() - start_time)
                
                return result
                
            except Exception as e:
                registry._metrics['errors'].labels(
                    agent_type=agent_type,
                    error_type=e.__class__.__name__
                ).inc()
                raise
                
        return wrapper
    return decorator