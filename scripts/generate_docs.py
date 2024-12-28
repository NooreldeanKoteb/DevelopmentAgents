import os
from pathlib import Path

def generate_docs():
    """Generate all documentation files."""
    
    # Create docs directory structure
    docs_dir = Path("docs")
    docs_dir.mkdir(exist_ok=True)
    
    api_dir = docs_dir / "api"
    api_dir.mkdir(exist_ok=True)
    
    guides_dir = docs_dir / "guides"
    guides_dir.mkdir(exist_ok=True)
    
    # Core documentation content
    core_guide = """# AI Development System Usage Guide

Core Configuration System
------------------------

Settings Management:
from core.config import get_settings

# Get settings instance
settings = get_settings()

# Access settings
api_key = settings.OPENAI_API_KEY
debug_mode = settings.DEBUG
redis_url = settings.REDIS_URL

OpenAI Integration System
------------------------

Basic Usage:
from core.openai import OpenAIClient

async def example():
    client = OpenAIClient()
    response = await client.get_completion(
        prompt="Generate a JSON object with user information"
    )
    data = response.content
    print(f"Response: {data}")

Message Bus System
-----------------

Basic Usage:
from core.messaging import MessageBroker, Message, MessagePriority

# Initialize broker
broker = MessageBroker()

# Define a message handler
async def handle_task_message(message: Message):
    print(f"Processing task: {message.payload}")

# Start the broker and subscribe to messages
async def main():
    # Subscribe to message types
    await broker.subscribe("task", handle_task_message)
    
    # Start the broker
    await broker.start()
    
    # Publish a message
    message = Message(
        sender="agent1",
        recipient="agent2",
        message_type="task",
        priority=MessagePriority.HIGH,
        payload={"task": "analyze_code", "file": "main.py"}
    )
    
    await broker.publish(message)

Advanced Message Bus Features
---------------------------

# Message with different priorities
urgent_message = Message(
    sender="security_agent",
    recipient="Director",
    message_type="security_alert",
    priority=MessagePriority.CRITICAL,
    payload={"alert": "vulnerability_detected", "severity": "high"}
)

# Check queue statistics
from core.messaging import QueueManager

async def check_queues():
    queue_manager = QueueManager()
    stats = await queue_manager.get_queue_stats()
    print(f"Queue stats: {stats}")
    
    failed = await queue_manager.get_failed_messages()
    print(f"Failed messages: {len(failed)}")

Message Bus Error Handling:
from core.messaging.errors import MessageBusError

try:
    await broker.publish(message)
except MessageBusError as e:
    print(f"Error: {e.message}")
    print(f"Code: {e.code}")
    print(f"Details: {e.details}")

Message Status Reference:
- PENDING: Message is queued
- DELIVERED: Message reached the recipient
- PROCESSING: Message is being processed
- COMPLETED: Message was successfully processed
- FAILED: Message processing failed
- RETRYING: Message is being retried

Message Priority Levels:
- LOW: Background tasks
- NORMAL: Standard operations
- HIGH: Important operations
- CRITICAL: Urgent operations

Best Practices
-------------

1. Configuration
   - Always use the settings system instead of hardcoding values
   - Keep sensitive information in environment variables

2. OpenAI Integration
   - Use appropriate temperature for the task
   - Monitor token usage and costs
   - Implement proper error handling
   - Cache responses when possible

3. Message Bus
   - Always specify appropriate message priority
   - Include relevant metadata in messages
   - Implement proper error handling
   - Monitor queue statistics
   - Handle failed messages appropriately

4. General
   - Initialize logging at application startup
   - Use appropriate log levels
   - Monitor system performance
   - Follow async patterns

Schema Validation System
-----------------------

Basic Usage:
from core.schemas import SchemaValidator, AgentMessageSchema

# Initialize validator
validator = SchemaValidator()

# Example data
message_data = {
    "agent_id": "agent1",
    "message_type": "task_complete",
    "content": {"task_id": "123", "status": "success"},
    "schema_version": "1.0"
}

# Validate and transform
try:
    result = await validator.validate(
        data=message_data,
        schema_class=AgentMessageSchema,
        transform=True
    )
    
    if result.is_valid:
        processed_data = result.transformed_data or result.original_data
        print(f"Valid data: {processed_data}")
        
except SchemaValidationError as e:
    print(f"Validation failed: {e.message}")
    print(f"Details: {e.details}")

Schema Versioning:
# Schema versions
- V1 = "1.0"  # Base version
- V1_1 = "1.1"  # Minor update
- V2 = "2.0"  # Major update

# Custom schema example
from core.schemas import BaseSchema, SchemaVersion

class TaskSchema(BaseSchema):
    task_id: str
    task_type: str
    priority: int
    parameters: Dict[str, Any]
    dependencies: List[str] = []

Data Transformation:
# Automatic version transformation
result = await validator.validate(
    data=old_data,
    schema_class=NewSchemaVersion,
    transform=True  # Enable automatic transformation
)

# Manual transformation
transformer = SchemaTransformer()
new_data = await transformer.transform(
    data=old_data,
    from_version=SchemaVersion.V1,
    to_version=SchemaVersion.V2
)

Error Handling:
try:
    result = await validator.validate(data, schema_class)
except SchemaValidationError as e:
    print(f"Validation Error: {e.message}")
    print(f"Error Code: {e.code}")
    print(f"Details: {e.details}")
except SchemaTransformError as e:
    print(f"Transform Error: {e.message}")

Best Practices:
1. Always specify schema version
2. Use transformation for version migrations
3. Handle validation errors appropriately
4. Monitor validation failures
5. Keep schemas backwards compatible when possible
"""

    # Write core guide
    with open(docs_dir / "usage_guide.txt", "w") as f:
        f.write(core_guide)
    
    print("Documentation generated successfully at:")
    print(f"- {docs_dir}/usage_guide.txt")

if __name__ == "__main__":
    generate_docs() 