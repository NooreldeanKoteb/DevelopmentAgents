

# Core Monitoring System Documentation

## Overview
The monitoring system provides comprehensive tracking, logging, and metrics collection for the application. It includes structured logging, performance metrics, health checks, and alerting capabilities.

## Key Components

### 1. Logger
**Location**: `core/monitoring/logger.py`

Custom JSON-formatted logger with structured logging support.

**Key Features**:
- JSON-formatted logs
- Log level management
- Context tracking
- Metadata support
- Performance logging

**Usage Example**:
```python
from core.monitoring import CoreLogger

logger = CoreLogger()
logger.info("User action completed", extra={
    "user_id": "123",
    "action": "login",
    "duration_ms": 150
})
```

### 2. Metrics
**Location**: `core/monitoring/metrics.py`

Handles collection and reporting of system metrics.

**Key Features**:
- Counter metrics
- Gauge metrics
- Histogram metrics
- Custom metrics
- Prometheus integration

**Usage Example**:
```python
from core.monitoring import CoreMetrics

metrics = CoreMetrics()
metrics.increment("api_requests_total", labels={"endpoint": "/users"})
metrics.observe("request_duration_seconds", 0.45)
```

### 3. Health Checks
**Location**: `core/monitoring/health.py`

System health monitoring and reporting.

**Key Features**:
- Service health checks
- Dependency checks
- Resource monitoring
- Status reporting
- Alert triggering

**Usage Example**:
```python
from core.monitoring import HealthCheck

health = HealthCheck()
status = await health.check_all()
if not status.is_healthy:
    await alert_admin(status.details)
```

## Metric Types

1. **System Metrics**:
```python
SYSTEM_METRICS = {
    "cpu_usage": Gauge("cpu_usage_percent"),
    "memory_usage": Gauge("memory_usage_bytes"),
    "disk_usage": Gauge("disk_usage_percent"),
    "open_files": Gauge("open_files_total")
}
```

2. **Application Metrics**:
```python
APP_METRICS = {
    "requests_total": Counter("http_requests_total"),
    "request_duration": Histogram("http_request_duration_seconds"),
    "active_users": Gauge("active_users_total"),
    "error_rate": Counter("error_rate_total")
}
```

## Logging Levels

```python
LOG_LEVELS = {
    "DEBUG": 10,
    "INFO": 20,
    "WARNING": 30,
    "ERROR": 40,
    "CRITICAL": 50
}
```

## Best Practices

1. **Structured Logging**:
```python
logger.info("Task completed", extra={
    "task_id": task.id,
    "duration": duration,
    "status": "success",
    "metadata": task.metadata
})
```

2. **Metric Collection**:
```python
@metrics.track_duration("function_duration_seconds")
async def monitored_function():
    # Function code here
    pass
```

3. **Health Checking**:
```python
async def check_service_health():
    health_status = {
        "database": await check_database(),
        "cache": await check_redis(),
        "api": await check_external_apis()
    }
    return all(health_status.values())
```

## Error Handling

Custom error types:
- MonitoringError: Base monitoring error
- MetricError: Metric collection errors
- LoggingError: Logging system errors
- HealthCheckError: Health check errors

## Performance Considerations

1. **Logging Performance**:
- Use appropriate log levels
- Batch log writes
- Implement log rotation
- Monitor log volume

2. **Metric Collection**:
- Use efficient metric types
- Implement sampling when needed
- Buffer metric updates
- Regular metric cleanup

3. **Health Checks**:
- Implement caching
- Use timeouts
- Parallel health checks
- Minimize check frequency

## Integration Points

The monitoring system integrates with:
1. Prometheus for metrics
2. ELK stack for logs
3. Alert management systems
4. Dashboard systems
5. Performance monitoring tools

## Common Usage Patterns

1. **Request Tracking**:
```python
@metrics.track_request
async def handle_request(request):
    with logger.context(request_id=request.id):
        try:
            result = await process_request(request)
            metrics.increment("successful_requests")
            return result
        except Exception as e:
            metrics.increment("failed_requests")
            logger.error("Request failed", exc_info=e)
            raise
```

2. **Resource Monitoring**:
```python
async def monitor_resources():
    while True:
        metrics.gauge("memory_usage").set(get_memory_usage())
        metrics.gauge("cpu_usage").set(get_cpu_usage())
        await asyncio.sleep(60)
```

3. **Performance Tracking**:
```python
@metrics.track_duration("operation_duration")
async def tracked_operation():
    start_time = time.time()
    try:
        await perform_operation()
    finally:
        logger.info("Operation completed", extra={
            "duration": time.time() - start_time
        })
```

## Alerting Configuration

```python
ALERT_RULES = {
    "high_error_rate": {
        "metric": "error_rate_total",
        "threshold": 0.05,
        "duration": "5m",
        "severity": "critical"
    },
    "high_latency": {
        "metric": "request_duration_seconds",
        "threshold": 1.0,
        "duration": "1m",
        "severity": "warning"
    }
}
```

## Development Guidelines

1. Always include relevant context in logs
2. Use appropriate metric types
3. Implement proper error handling
4. Monitor system impact
5. Maintain consistent naming
6. Document metric meanings
7. Regular metric maintenance

## Testing

The system includes tests for:
- Log formatting and levels
- Metric collection accuracy
- Health check functionality
- Alert triggering
- Performance impact

For more detailed examples and advanced usage patterns, refer to the tests in `tests/core/monitoring/`.

## Dashboard Integration

The monitoring system provides data for:
- System health dashboards
- Performance metrics
- Error tracking
- Resource utilization
- Custom business metrics

Remember to configure appropriate retention policies and aggregation rules for long-term metric storage and analysis.
