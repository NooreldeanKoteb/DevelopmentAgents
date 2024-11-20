from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import json
from redis.asyncio import Redis, ConnectionPool
from contextlib import asynccontextmanager
from typing import AsyncGenerator
from .errors import MemoryError

class Memory:
    """Agent memory management using Redis."""
    
    def __init__(self, agent_id: str, redis_url: str = "redis://localhost:6379/0"):
        self.agent_id = agent_id
        self.pool = ConnectionPool.from_url(
            redis_url,
            decode_responses=True
        )
        
    @asynccontextmanager
    async def get_connection(self) -> AsyncGenerator[Redis, None]:
        """Get Redis connection from pool."""
        conn = Redis(connection_pool=self.pool)
        try:
            yield conn
        finally:
            await conn.close()
            
    async def store(self, key: str, value: Any, ttl: Optional[timedelta] = None) -> None:
        """Store data in memory."""
        try:
            memory_key = f"memory:{self.agent_id}:{key}"
            data = json.dumps(value)
            
            async with self.get_connection() as redis:
                if ttl:
                    await redis.setex(memory_key, int(ttl.total_seconds()), data)
                else:
                    await redis.set(memory_key, data)
                    
        except Exception as e:
            raise MemoryError(f"Failed to store memory: {str(e)}")
            
    async def retrieve(self, key: str) -> Optional[Any]:
        """Retrieve data from memory."""
        try:
            memory_key = f"memory:{self.agent_id}:{key}"
            
            async with self.get_connection() as redis:
                data = await redis.get(memory_key)
                if data:
                    return json.loads(data)
                return None
                
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
        