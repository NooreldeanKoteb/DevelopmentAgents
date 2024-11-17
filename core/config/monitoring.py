from prometheus_client import Counter, Histogram, start_http_server
from functools import wraps
import time
from .settings import get_settings

# Define metrics
REQUEST_COUNT = Counter(
    'request_total',
    'Total request count',
    ['method', 'endpoint', 'status']
)

REQUEST_LATENCY = Histogram(
    'request_latency_seconds',
    'Request latency in seconds',
    ['method', 'endpoint']
)

AGENT_OPERATIONS = Counter(
    'agent_operations_total',
    'Total agent operations',
    ['agent_type', 'operation', 'status']
)

def initialize_monitoring():
    """Start the monitoring HTTP server."""
    settings = get_settings()
    if settings.ENABLE_METRICS:
        start_http_server(settings.METRICS_PORT)

def monitor_operation(agent_type: str, operation: str):
    """Decorator to monitor agent operations."""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = await func(*args, **kwargs)
                AGENT_OPERATIONS.labels(
                    agent_type=agent_type,
                    operation=operation,
                    status="success"
                ).inc()
                return result
            except Exception as e:
                AGENT_OPERATIONS.labels(
                    agent_type=agent_type,
                    operation=operation,
                    status="error"
                ).inc()
                raise e
            finally:
                duration = time.time() - start_time
                REQUEST_LATENCY.labels(
                    method=agent_type,
                    endpoint=operation
                ).observe(duration)
        return wrapper
    return decorator 