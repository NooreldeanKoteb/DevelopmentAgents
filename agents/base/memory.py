from typing import Any, Optional, Dict, List
from datetime import datetime, timedelta
import json
from redis.asyncio import Redis
from core.config import get_settings

class AgentMemory:
    """Manages agent memory storage and retrieval."""
    
    def __init__(self, agent_id: str):
        self.agent_id = agent_id
        self.settings = get_settings()
        self.redis = Redis.from_url(
            self.settings.REDIS_URL,
            decode_responses=True
        )
        self.ttl = timedelta(days=7)
        
    async def store(
        self,
        key: str,
        value: Any,
        ttl: Optional[timedelta] = None
    ) -> None:
        """Store data in memory."""
        memory_key = f"agent:{self.agent_id}:memory:{key}"
        try:
            serialized = json.dumps(value)
            await self.redis.setex(
                memory_key,
                ttl or self.ttl,
                serialized
            )
        except Exception as e:
            raise MemoryError(f"Failed to store memory: {str(e)}")
            
    async def retrieve(self, key: str) -> Optional[Any]:
        """Retrieve data from memory."""
        memory_key = f"agent:{self.agent_id}:memory:{key}"
        try:
            data = await self.redis.get(memory_key)
            return json.loads(data) if data else None
        except Exception as e:
            raise MemoryError(f"Failed to retrieve memory: {str(e)}")
            
    async def list_memories(
        self,
        pattern: str = "*",
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """List stored memories."""
        try:
            keys = await self.redis.keys(
                f"agent:{self.agent_id}:memory:{pattern}"
            )
            memories = []
            
            for key in keys[:limit]:
                data = await self.redis.get(key)
                if data:
                    memories.append({
                        "key": key.split(":")[-1],
                        "value": json.loads(data)
                    })
                    
            return memories
        except Exception as e:
            raise MemoryError(f"Failed to list memories: {str(e)}")
            
    async def clear(self, pattern: str = "*") -> None:
        """Clear memories matching pattern."""
        try:
            keys = await self.redis.keys(
                f"agent:{self.agent_id}:memory:{pattern}"
            )
            if keys:
                await self.redis.delete(*keys)
        except Exception as e:
            raise MemoryError(f"Failed to clear memories: {str(e)}")
        