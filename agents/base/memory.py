from typing import Any, Dict, List, Optional
import redis.asyncio as redis
from datetime import datetime, timedelta
from .errors import MemoryError

class Memory:
    def __init__(self, redis_url: str = "redis://localhost:6379/0"):
        """Initialize memory with Redis connection."""
        self.redis = redis.from_url(redis_url)
        
    async def store(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Store a value in memory."""
        try:
            await self.redis.set(key, value, ex=ttl)
        except Exception as e:
            raise MemoryError(f"Failed to store memory: {str(e)}")
            
    async def retrieve(self, key: str) -> Any:
        """Retrieve a value from memory."""
        try:
            value = await self.redis.get(key)
            return value
        except Exception as e:
            raise MemoryError(f"Failed to retrieve memory: {str(e)}")
            
    async def clear(self) -> None:
        """Clear all memories."""
        try:
            await self.redis.flushdb()
        except Exception as e:
            raise MemoryError(f"Failed to clear memories: {str(e)}")
            
    async def list(self) -> List[str]:
        """List all memory keys."""
        try:
            keys = await self.redis.keys("*")
            return [k.decode() for k in keys]
        except Exception as e:
            raise MemoryError(f"Failed to list memories: {str(e)}")
        