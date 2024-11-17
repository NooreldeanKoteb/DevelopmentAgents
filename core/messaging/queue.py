from typing import List, Optional
from datetime import datetime, timedelta
import redis.asyncio as redis
from .schemas import Message, MessagePriority, MessageStatus
from core.config import get_settings

class QueueManager:
    """Manages message queues and their states."""
    
    def __init__(self):
        self.settings = get_settings()
        self.redis = redis.from_url(self.settings.REDIS_URL)
    
    async def get_queue_length(self, priority: MessagePriority) -> int:
        """Get the length of a specific priority queue."""
        return await self.redis.llen(f"queue:{priority.value}")
    
    async def get_queue_stats(self) -> dict:
        """Get statistics for all queues."""
        stats = {}
        for priority in MessagePriority:
            stats[priority.value] = {
                "length": await self.get_queue_length(priority),
                "processing": await self.redis.scard(f"processing:{priority.value}")
            }
        return stats
    
    async def clear_queue(self, priority: MessagePriority):
        """Clear a specific priority queue."""
        await self.redis.delete(f"queue:{priority.value}")
    
    async def get_failed_messages(self, limit: int = 100) -> List[Message]:
        """Get list of failed messages."""
        failed_keys = await self.redis.keys("message:status:*")
        failed_messages = []
        
        for key in failed_keys[:limit]:
            status_data = await self.redis.hgetall(key)
            if status_data.get("status") == MessageStatus.FAILED.value:
                message_id = key.split(":")[-1]
                message_data = await self.redis.get(f"message:{message_id}")
                if message_data:
                    failed_messages.append(Message.model_validate_json(message_data))
        
        return failed_messages 
    
    async def move_to_dead_letter(self, message: Message):
        """Move failed message to dead letter queue."""
        await self.redis.lpush(
            "queue:dead_letter",
            message.model_dump_json()
        )
        
    async def process_dead_letter_queue(self):
        """Process messages in dead letter queue."""
        while message_data := await self.redis.rpop("queue:dead_letter"):
            message = Message.model_validate_json(message_data)
            # Implement dead letter queue processing logic