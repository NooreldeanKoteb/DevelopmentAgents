from typing import Dict, Any, Optional, List, Union
from datetime import timedelta
from redis.asyncio import Redis
import json
from agents.base.errors import MemoryError

class Memory:
    def __init__(self, redis_client: Optional[Redis] = None, redis_url: Optional[str] = None):
        """Initialize Memory with either a Redis client or URL."""
        if redis_client:
            self.redis = redis_client
        elif redis_url:
            self.redis = Redis.from_url(redis_url, decode_responses=True)
        else:
            raise ValueError("Either redis_client or redis_url must be provided")
        self._initialized = False

    async def initialize(self) -> None:
        """Initialize memory system."""
        if self._initialized:
            return
        await self.redis.ping()
        self._initialized = True

    async def store(self, key: str, value: Any, ttl: Optional[timedelta] = None) -> None:
        """Store data in memory."""
        serialized = json.dumps(value)
        if ttl:
            await self.redis.setex(key, int(ttl.total_seconds()), serialized)
        else:
            await self.redis.set(key, serialized)

    async def retrieve(self, key: str, raise_error: bool = False) -> Optional[Any]:
        """Retrieve data from memory."""
        value = await self.redis.get(key)
        if value is None:
            if raise_error:
                raise MemoryError(f"Key {key} not found")
            return None
        return json.loads(value)

    async def list_memories(self, pattern: str = "*") -> List[Dict[str, Any]]:
        """List all memories matching the pattern."""
        try:
            # Ensure pattern is a string
            pattern = str(pattern)
            keys = await self.redis.keys(pattern)
            
            if not keys:
                return []
            
            # Get all values in a pipeline
            pipeline = self.redis.pipeline()
            for key in keys:
                pipeline.get(key)
            
            values = await pipeline.execute()
            
            result = []
            for key, value in zip(keys, values):
                if value is not None:
                    try:
                        parsed_value = json.loads(value)
                    except json.JSONDecodeError:
                        parsed_value = value
                    
                    # Clean key - handle both bytes and string with byte markers
                    clean_key = key
                    if isinstance(clean_key, bytes):
                        clean_key = clean_key.decode('utf-8')
                    else:
                        # Remove any remaining byte string markers
                        clean_key = str(clean_key).replace("b'", "").replace("'", "")
                    
                    result.append({
                        "key": clean_key,
                        "value": parsed_value
                    })
            
            return sorted(result, key=lambda x: x["key"])
        except Exception as e:
            # Log error and return empty list
            print(f"Error in list_memories: {str(e)}")
            return []

    async def clear(self, key: Optional[str] = None) -> None:
        """Clear specific memory or all memories if no key provided."""
        if key:
            await self.redis.delete(key)
        else:
            await self.redis.flushdb()

    async def cleanup(self) -> None:
        """Cleanup resources."""
        if hasattr(self, 'redis') and self.redis is not None:
            try:
                # First clear any pending operations
                await self.redis.flushdb()
                # Then close the connection pool
                if hasattr(self.redis, 'connection_pool'):
                    await self.redis.connection_pool.disconnect()
                # Finally close the client
                await self.redis.aclose()
                # Remove reference to redis client
                delattr(self, 'redis')
            except Exception as e:
                print(f"Error during Redis cleanup: {str(e)}")
        