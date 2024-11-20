from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import json
from redis.asyncio import Redis
from core.messaging import Message
from core.config import get_settings

class MessageStore:
    """Persistent storage for message history."""
    
    def __init__(self):
        settings = get_settings()
        self.redis = Redis.from_url(settings.REDIS_URL, decode_responses=True)
        self.retention_days = 7
        
    async def store_message(self, message: Message) -> None:
        """Store a message with TTL."""
        key = f"messages:{message.topic}:{message.id}"
        await self.redis.setex(
            key,
            timedelta(days=self.retention_days),
            json.dumps(message.model_dump())
        )
        
        # Store in time index
        await self.redis.zadd(
            f"message_timeline:{message.topic}",
            {message.id: message.timestamp.timestamp()}
        )
        
    async def get_messages(
        self,
        topic: str,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: int = 100
    ) -> List[Message]:
        """Retrieve messages by time range."""
        min_score = start_time.timestamp() if start_time else "-inf"
        max_score = end_time.timestamp() if end_time else "+inf"
        
        message_ids = await self.redis.zrangebyscore(
            f"message_timeline:{topic}",
            min_score,
            max_score,
            start=0,
            num=limit
        )
        
        messages = []
        for msg_id in message_ids:
            data = await self.redis.get(f"messages:{topic}:{msg_id}")
            if data:
                messages.append(Message.model_validate(json.loads(data)))
                
        return messages 