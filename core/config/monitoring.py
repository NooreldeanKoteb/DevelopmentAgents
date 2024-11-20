import functools
import time
from typing import Callable, Any
from prometheus_client import Counter, Histogram

# Define metrics
REQUEST_COUNT = Counter(
    'agent_requests_total',
    'Total requests by agent and operation type',
    ['agent_type', 'operation']
)

LATENCY = Histogram(
    'agent_operation_duration_seconds',
    'Operation duration in seconds',
    ['agent_type', 'operation']
)

ERROR_COUNT = Counter(
    'agent_errors_total',
    'Total errors by agent and error type',
    ['agent_type', 'error_type']
)

def monitor_operation(agent_type: str, operation: str) -> Callable:
    """Decorator to monitor agent operations."""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            REQUEST_COUNT.labels(agent_type=agent_type, operation=operation).inc()
            
            start_time = time.time()
            try:
                result = await func(*args, **kwargs)
                LATENCY.labels(
                    agent_type=agent_type,
                    operation=operation
                ).observe(time.time() - start_time)
                return result
            except Exception as e:
                ERROR_COUNT.labels(
                    agent_type=agent_type,
                    error_type=type(e).__name__
                ).inc()
                raise
                
        return wrapper
    return decorator