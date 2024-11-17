import asyncio
import json
from typing import Optional, Callable, Dict, Any
import redis.asyncio as redis
from datetime import datetime, timedelta
from uuid import UUID
from .queue import QueueManager
from .schemas import Message, MessagePriority, MessageStatus
from core.config import get_settings, monitor_operation
from .errors import MessageBusError

class MessageBroker:
    """Handles message routing and queue management."""
    
    def __init__(self):
        self.settings = get_settings()
        self.redis = redis.from_url(self.settings.REDIS_URL)
        self.handlers: Dict[str, Callable] = {}
        self.processing = False
        
    async def start(self):
        """Start the message broker."""
        self.processing = True
        asyncio.create_task(self._process_queues())
    
    async def stop(self):
        """Stop the message broker."""
        self.processing = False
    
    @monitor_operation(agent_type="message_broker", operation="publish")
    async def publish(self, message: Message) -> bool:
        """Publish a message to the appropriate queue."""
        try:
            # Serialize message
            message_data = message.model_dump_json()
            
            # Get queue name based on priority
            queue_name = f"queue:{message.priority.value}"
            
            # Add to queue
            await self.redis.lpush(queue_name, message_data)
            
            # Store message status
            await self._update_message_status(message.id, MessageStatus.PENDING)
            
            return True
            
        except Exception as e:
            raise MessageBusError(
                message="Failed to publish message",
                code="publish_error",
                details={"message_id": str(message.id), "error": str(e)}
            )
    
    async def subscribe(self, message_type: str, handler: Callable):
        """Subscribe to a specific message type."""
        self.handlers[message_type] = handler
    
    async def _process_queues(self):
        """Process messages from queues based on priority."""
        priority_queues = [
            f"queue:{MessagePriority.CRITICAL.value}",
            f"queue:{MessagePriority.HIGH.value}",
            f"queue:{MessagePriority.NORMAL.value}",
            f"queue:{MessagePriority.LOW.value}"
        ]
        
        while self.processing:
            for queue in priority_queues:
                # Get message from queue
                message_data = await self.redis.rpop(queue)
                if message_data:
                    await self._handle_message(message_data)
            
            await asyncio.sleep(0.1)  # Prevent CPU overload
    
    async def _handle_message(self, message_data: bytes):
        """Handle a single message."""
        try:
            # Parse message
            message_dict = json.loads(message_data)
            message = Message.model_validate(message_dict)
            
            # Update status
            await self._update_message_status(message.id, MessageStatus.PROCESSING)
            
            # Get handler
            handler = self.handlers.get(message.message_type)
            if not handler:
                raise MessageBusError(
                    message=f"No handler for message type: {message.message_type}",
                    code="no_handler",
                    details={"message_id": str(message.id)}
                )
            
            # Execute handler
            try:
                await handler(message)
                await self._update_message_status(message.id, MessageStatus.COMPLETED)
            except Exception as e:
                await self._handle_message_failure(message, str(e))
                
        except Exception as e:
            # Log error and update status
            print(f"Error processing message: {str(e)}")
            if message:
                await self._update_message_status(message.id, MessageStatus.FAILED)
    
    async def _handle_message_failure(self, message: Message, error: str):
        """Handle message processing failure."""
        if message.retry_count < message.max_retries:
            # Increment retry count
            message.retry_count += 1
            message.status = MessageStatus.RETRYING
            
            # Add back to queue with delay
            delay = 2 ** message.retry_count  # Exponential backoff
            await asyncio.sleep(delay)
            await self.publish(message)
        else:
            # Mark as failed
            await self._update_message_status(message.id, MessageStatus.FAILED)
            
            # Store error details
            await self.redis.hset(
                f"message:errors:{message.id}",
                mapping={"error": error, "timestamp": datetime.utcnow().isoformat()}
            )
    
    async def _update_message_status(self, message_id: UUID, status: MessageStatus):
        """Update and track message status."""
        
    async def _persist_message(self, message: Message):
        """Persist message to storage for reliability."""
        await self.redis.set(
            f"message:{message.id}",
            message.model_dump_json(),
            ex=86400  # 24 hour expiry
        )
        
    async def get_message_history(self, message_id: UUID) -> Dict[str, Any]:
        """Get message history including all status changes."""
        history = await self.redis.hgetall(f"message:history:{message_id}")
        return {
            "message": await self.redis.get(f"message:{message_id}"),
            "status_history": history,
            "error": await self.redis.hgetall(f"message:errors:{message_id}")
        }
    
    async def acknowledge_message(self, message_id: UUID):
        """Acknowledge message processing completion."""
        await self._update_message_status(message_id, MessageStatus.DELIVERED)
        await self.redis.hset(
            f"message:history:{message_id}",
            mapping={
                "acknowledged_at": datetime.utcnow().isoformat(),
                "status": MessageStatus.DELIVERED.value
            }
        )
    