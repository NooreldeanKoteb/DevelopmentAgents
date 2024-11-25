from typing import Any, Dict, List, Optional
import redis.asyncio as redis
from datetime import datetime, timedelta
import json
from .errors import MemoryError

class Memory:
    def __init__(self, redis_url: str = "redis://localhost:6379/0"):
        """Initialize memory with Redis connection."""
        self.redis = redis.from_url(redis_url)
        
    async def store(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Store a value in memory."""
        try:
            # Serialize dict/complex objects to JSON
            if isinstance(value, (dict, list)):
                value = json.dumps(value)
            await self.redis.set(key, value, ex=ttl)
        except Exception as e:
            raise MemoryError(f"Failed to store memory: {str(e)}")
            
    async def retrieve(self, key: str, raise_error: bool = False) -> Any:
        """Retrieve a value from memory."""
        try:
            value = await self.redis.get(key)
            if value is None and raise_error:
                raise MemoryError(f"Key not found: {key}")
            if value:
                try:
                    # Try to deserialize JSON
                    return json.loads(value)
                except json.JSONDecodeError:
                    # If not JSON, return as string
                    return value.decode()
            return None
        except Exception as e:
            raise MemoryError(f"Failed to retrieve memory: {str(e)}")
            
    async def clear(self, pattern: Optional[str] = None) -> None:
        """Clear memories matching pattern or all if no pattern."""
        try:
            if pattern:
                keys = await self.redis.keys(pattern)
                if keys:
                    await self.redis.delete(*keys)
            else:
                await self.redis.flushdb()
        except Exception as e:
            raise MemoryError(f"Failed to clear memories: {str(e)}")
            
    async def list_memories(self, pattern: str = "*") -> List[Dict[str, Any]]:
        """List all memory keys matching pattern."""
        try:
            keys = await self.redis.keys(pattern)
            memories = []
            for key in keys:
                value = await self.retrieve(key)
                memories.append({"key": key.decode(), "value": value})
            return memories
        except Exception as e:
            raise MemoryError(f"Failed to list memories: {str(e)}")
        