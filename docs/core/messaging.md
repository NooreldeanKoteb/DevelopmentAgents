# Core Messaging System Documentation

## Overview
The core messaging system provides a robust infrastructure for inter-service communication within the application. It implements a publish/subscribe pattern with support for message queuing, prioritization, and error handling.

## Key Components

### 1. Message Class
**Location**: `core/messaging/message.py`

The base message model for all communication.

**Key Features**:
- Unique message ID generation using UUID4
- Topic-based routing
- Content payload support (Dict[str, Any])
- Metadata support for additional information
- Automatic timestamp tracking
- Sender/Recipient tracking
- Pydantic model validation

**Usage Example**:
```python
message = Message(
    topic="user.created",
    content={"user_id": "123", "email": "user@example.com"},
    sender="auth_service"
)
```

### 2. Message Broker
**Location**: `core/messaging/broker.py`

Handles message routing and delivery between services.

**Key Features**:
- Asynchronous message publishing
- Topic-based subscription system
- Comprehensive error handling
- Message monitoring integration
- Automatic resource cleanup
- Support for message priorities

**Usage Example**:
```python
broker = MessageBroker()

# Subscribe to messages
async def handle_user_created(message):
    print(f"New user created: {message.content}")

await broker.subscribe("user.created", handle_user_created)

# Publish a message
await broker.publish(message)
```

### 3. Message Queue
**Location**: `core/messaging/queue.py`

Implements FIFO queue for message processing.

**Key Features**:
- Asynchronous queue operations
- Configurable timeout support
- Maximum queue size management
- Priority queue implementation
- Dead letter queue handling
- Queue statistics tracking

### 4. Message Schemas
**Location**: `core/messaging/schemas.py`

**Key Enums**:
```python
class MessagePriority(str, Enum):
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    CRITICAL = "critical"

class MessageStatus(str, Enum):
    PENDING = "pending"
    DELIVERED = "delivered"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    RETRYING = "retrying"
```

## Error Handling

**Location**: `core/messaging/errors.py`

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

## Integration Points

The messaging system integrates with:
1. Redis for message persistence
2. Monitoring system for metrics
3. Logging system for message tracking
4. Schema validation system

## Performance Considerations

1. **Queue Management**:
   - Regular monitoring of queue sizes
   - Appropriate timeout configurations
   - Dead letter queue processing

2. **Resource Management**:
   - Proper broker connection cleanup
   - Test cleanup implementation
   - Subscription management

3. **Message Optimization**:
   - Concise message payloads
   - Efficient data structures
   - Large payload handling

## Testing

The system includes tests for:
- Basic publish/subscribe operations
- Error handling scenarios
- Timeout behaviors
- Queue operations
- Resource cleanup
- Message validation

## Monitoring

Built-in monitoring for:
- Queue statistics and metrics
- Message processing performance
- Error rate tracking
- System health monitoring

## Common Usage Patterns

1. **Simple Message Publishing**:
```python
await broker.publish(Message(
    topic="notifications",
    content={"type": "alert", "message": "System update required"},
    sender="system"
))
```

2. **Message Handler Setup**:
```python
async def handle_notifications(message: Message):
    if message.content["type"] == "alert":
        await send_alert(message.content["message"])

await broker.subscribe("notifications", handle_notifications)
```

3. **Queue Processing**:
```python
async def process_queue():
    while True:
        message = await queue.get()
        if message:
            await process_message(message)
        await asyncio.sleep(0.1)
```

For more detailed examples and advanced usage patterns, refer to the tests in `tests/core/messaging/`.
