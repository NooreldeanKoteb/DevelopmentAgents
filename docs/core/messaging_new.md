Here's a comprehensive guide to the messaging system:

```markdown
# Agent Messaging System Guide

## Overview
The messaging system enables asynchronous communication between agents using a publish/subscribe (pub/sub) pattern. It consists of three main components:
- Message: The data structure for communication
- MessageBroker: Handles message routing and delivery
- MessageQueue: Manages message queues and persistence

## Message Structure
```python
class Message:
    topic: str              # Routing topic (e.g., "project.new")
    content: Dict[str, Any] # Message payload
    sender: str             # Sender agent ID
    recipient: Optional[str] # Specific recipient (optional)
    priority: Priority      # Message priority
    metadata: Dict[str, Any] # Additional message context
    timestamp: datetime     # Message creation time
```

## Core Topics
Common message topics for agent communication:
- `project.new`: New project creation
- `project.update`: Project status updates
- `task.status`: Task status changes
- `agent.status`: Agent state updates
- `resource.status`: Resource availability updates

## Publishing Messages

### Basic Publishing
```python
# From any agent
await self.message_broker.publish(Message(
    topic="task.status",
    content={"task_id": "123", "status": "completed"},
    sender=self.agent_id
))
```

### With Priority
```python
await self.message_broker.publish(Message(
    topic="project.new",
    content=project_data,
    sender=self.agent_id,
    priority=Priority.HIGH
))
```

## Subscribing to Messages

### Basic Subscription
```python
# In agent initialization
async def initialize(self):
    await self.message_broker.subscribe(
        "task.status", 
        self.process_message
    )
```

### Multiple Topic Subscription
```python
topics = ["project.new", "project.update", "task.status"]
for topic in topics:
    await self.message_broker.subscribe(topic, self.process_message)
```

## Message Processing

### Handler Implementation
```python
async def process_message(self, message: Message) -> Any:
    handlers = {
        "project.new": self._handle_new_project,
        "task.status": self._handle_task_status,
        "agent.status": self._handle_agent_status
    }
    
    handler = handlers.get(message.topic)
    if handler:
        return await handler(message)
    raise MessageHandlerError(f"No handler for topic: {message.topic}")
```

## Queue Management

### Priority Queues
```python
# Check queue status
queue_stats = await queue_manager.get_queue_stats()

# Clear specific queue
await queue_manager.clear_queue(Priority.LOW)

# Get failed messages
failed = await queue_manager.get_failed_messages()
```

### Dead Letter Queue
```python
# Move failed message to DLQ
await queue_manager.move_to_dead_letter(failed_message)

# Process DLQ
await queue_manager.process_dead_letter_queue()
```

## Error Handling

### Message Broker Error Handling
```python
async def _safe_handle(self, handler, message):
    try:
        await handler(message)
    except Exception as e:
        await self._handle_error(e)
```

### Custom Error Handlers
```python
async def error_handler(error: Exception):
    logging.error(f"Message processing error: {str(error)}")
    # Additional error handling logic

message_broker.on_error(error_handler)
```

## Best Practices

1. **Topic Naming**:
   - Use dot notation for hierarchy: `domain.action`
   - Keep names descriptive and consistent
   - Example: `project.status.update`

2. **Message Content**:
   - Include all necessary context
   - Keep payload focused and relevant
   - Use proper data types

3. **Error Handling**:
   - Always implement error handlers
   - Use dead letter queues for failed messages
   - Log errors with context

4. **Resource Management**:
   - Clean up subscriptions when done
   - Monitor queue sizes
   - Implement timeouts for message processing

5. **Performance**:
   - Use appropriate priority levels
   - Implement message batching when possible
   - Monitor message processing times

## Cleanup and Shutdown

```python
async def cleanup(self):
    # Unsubscribe from topics
    for topic in self.subscribed_topics:
        await self.message_broker.unsubscribe(topic, self.process_message)
    
    # Clean up message broker
    await self.message_broker.cleanup()
```

## Monitoring

The messaging system includes built-in monitoring:
- Queue lengths
- Processing times
- Error rates
- Message volumes
- Queue statistics

## Example: Complete Agent Communication

```python
class AgentA:
    async def initialize(self):
        await self.message_broker.subscribe("task.request", self.handle_task)
        
    async def request_task(self, task_data):
        await self.message_broker.publish(Message(
            topic="task.request",
            content=task_data,
            sender=self.agent_id
        ))
        
class AgentB:
    async def initialize(self):
        await self.message_broker.subscribe("task.response", self.handle_response)
        
    async def handle_task(self, message: Message):
        result = await self.process_task(message.content)
        await self.message_broker.publish(Message(
            topic="task.response",
            content=result,
            sender=self.agent_id,
            recipient=message.sender
        ))
```

This messaging system provides a robust foundation for agent communication while maintaining loose coupling and scalability.
```
