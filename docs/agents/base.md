# Base Agent System Documentation

## Overview
The base agent system provides the foundational framework for all agent types in the system. It implements core functionality for message handling, task execution, memory management, and error handling that all specialized agents inherit from.

## Key Components

### 1. Base Agent
**Location**: `agents/base/base_agent.py`

The core agent class that all other agents inherit from.

**Key Features**:
- Message processing
- Task execution
- Error handling
- Memory management
- Context tracking
- Logging integration

**Usage Example**:
```python
from agents.base import BaseAgent

class CustomAgent(BaseAgent):
    async def process_message(self, message: Message):
        await self.validate_message(message)
        result = await self.execute_task(message.content)
        await self.store_result(result)
```

### 2. Memory Management
**Location**: `agents/base/memory.py`

Handles agent memory and state management.

**Key Features**:
- State persistence
- Context management
- Memory cleanup
- Memory optimization
- Query capabilities

### 3. Message Handling
**Location**: `agents/base/message.py`

Manages inter-agent communication.

Reference to message system documentation:

````95:130:docs/core_messaging.md
Custom error types:
- MessageBusError: Base error class
- MessageValidationError: For schema validation errors
- MessageDeliveryError: For message delivery failures
- MessageHandlerError: For message handler execution errors

## Best Practices

1. **Message Creation**:
```python
message = Message(
    topic="service.event",
    content={"key": "value"},
    sender="service_name",
    metadata={"priority": "high"}
)
```

2. **Error Handling**:
```python
try:
    await broker.publish(message)
except MessageDeliveryError as e:
    logger.error(f"Failed to deliver message: {e}")
```

3. **Message Processing**:
```python
async def process_message(message: Message):
    try:
        await handle_message_content(message.content)
        message.status = MessageStatus.COMPLETED
    except Exception as e:
        message.status = MessageStatus.FAILED
        raise MessageHandlerError(f"Processing failed: {e}")
```
````


## Required Methods

All agents must implement:

```python
class BaseAgent(ABC):
    @abstractmethod
    async def process_message(self, message: Message) -> None:
        """Process incoming messages"""
        pass
        
    @abstractmethod
    async def execute_task(self, task: Task) -> Result:
        """Execute assigned tasks"""
        pass
        
    @abstractmethod
    async def handle_error(self, error: Exception) -> None:
        """Handle agent-specific errors"""
        pass
```

## Integration Points

The base agent integrates with core systems:

1. **Message Bus Integration**
```python
async def send_message(self, message: Message):
    try:
        await self.message_bus.publish(
            topic=message.topic,
            content=message.content,
            metadata={"agent_id": self.id}
        )
    except MessageBusError as e:
        await self.handle_error(e)
```

2. **Memory Integration**
```python
async def store_context(self, context: Dict[str, Any]):
    await self.memory.store(
        key=f"context:{self.id}",
        value=context,
        ttl=self.config.context_ttl
    )
```

## Error Handling

Custom error types:
```python
class AgentError(Exception):
    """Base agent error"""
    pass

class TaskExecutionError(AgentError):
    """Task execution failed"""
    pass

class MemoryError(AgentError):
    """Memory operation failed"""
    pass

class MessageProcessingError(AgentError):
    """Message processing failed"""
    pass
```

## Monitoring Integration

Reference to monitoring configuration:

````39:53:docs/core_monitoring.md
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
````


## Agent Configuration

```python
AGENT_CONFIG = {
    "memory": {
        "max_size": 1000,
        "ttl": 3600,
        "cleanup_interval": 300
    },
    "messaging": {
        "max_retries": 3,
        "retry_delay": 1.0,
        "timeout": 30
    },
    "execution": {
        "max_concurrent_tasks": 10,
        "task_timeout": 300,
        "backoff_factor": 2.0
    }
}
```

## Common Usage Patterns

1. **Task Execution Pattern**:
```python
async def execute_task(self, task: Task) -> Result:
    try:
        # Pre-execution setup
        await self.prepare_execution(task)
        
        # Execute task
        result = await self._execute(task)
        
        # Post-execution cleanup
        await self.cleanup_execution(task)
        
        return result
    except Exception as e:
        await self.handle_error(e)
        raise TaskExecutionError(f"Task execution failed: {e}")
```

2. **Memory Management Pattern**:
```python
async def manage_memory(self):
    while True:
        try:
            # Cleanup old entries
            await self.memory.cleanup()
            
            # Optimize storage
            if await self.memory.size() > self.config.memory.max_size:
                await self.memory.optimize()
                
            await asyncio.sleep(self.config.memory.cleanup_interval)
        except Exception as e:
            await self.handle_error(e)
```

## Development Guidelines

1. **Agent Implementation**:
- Inherit from BaseAgent
- Implement required methods
- Add proper error handling
- Include monitoring
- Document agent capabilities
- Add comprehensive tests

2. **Memory Usage**:
- Implement cleanup strategies
- Monitor memory usage
- Use appropriate TTLs
- Handle memory errors
- Regular optimization

3. **Message Handling**:
- Validate all messages
- Handle timeouts
- Implement retries
- Monitor message flow
- Log message errors

## Testing

The base agent includes tests for:
- Message processing
- Task execution
- Error handling
- Memory management
- State persistence
- Performance metrics

For specific agent implementations and examples, refer to the tests in `tests/agents/base/`.

## Agent Rules
Reference to agent rules:
```
.cursorrules
startLine: 147
endLine: 156
```

Remember to:
- Follow agent protocols
- Handle errors gracefully
- Monitor agent health
- Maintain agent state
- Document agent behavior
- Test thoroughly

This documentation provides a high-level overview of the base agent system. For specific implementation details, refer to the individual component documentation.
