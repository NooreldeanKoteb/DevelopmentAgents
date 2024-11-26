from typing import Optional, Dict, Any
import json
from datetime import datetime, timedelta
import redis.asyncio as aioredis
from core.config import get_settings
from redis.asyncio import Redis

class ResponseCache:
    """Caches OpenAI responses to reduce API calls."""
    
    def __init__(self, redis_client: Redis = None, redis_url: str = None):
        if redis_client:
            self.redis = redis_client
        else:
            url = redis_url or "redis://localhost:6379/0"
            self.redis = Redis.from_url(url, decode_responses=True)
        self.settings = get_settings()
        self.ttl = int(timedelta(hours=24).total_seconds())  # Convert to seconds
        
    async def get(self, key: str) -> Optional[Dict[str, Any]]:
        """Get cached response."""
        try:
            full_key = f"openai:cache:{key}"
            print(f"Checking cache for key: {full_key}")
            data = await self.redis.get(full_key)
            if data:
                print(f"Cache hit for key: {full_key}")
                return json.loads(data)
            print(f"Cache miss for key: {full_key}")
            return None
        except Exception as e:
            print(f"Error getting from cache: {str(e)}")
            return None
            
    async def set(self, key: str, value: Dict[str, Any]) -> None:
        """Cache a response."""
        try:
            full_key = f"openai:cache:{key}"
            print(f"Setting cache for key: {full_key}")
            serialized = json.dumps(value)
            await self.redis.setex(
                full_key,
                self.ttl,
                serialized
            )
            # Verify the cache was set
            cached = await self.redis.get(full_key)
            if cached:
                print(f"Successfully cached response for key: {full_key}")
            else:
                print(f"Failed to cache response for key: {full_key}")
        except Exception as e:
            print(f"Error setting cache: {str(e)}")
            raise  # Don't fail silently anymore
            
    async def clear(self) -> None:
        """Clear all cached responses."""
        try:
            # Get all keys matching the pattern
            pattern = "openai:cache:*"
            keys = await self.redis.keys(pattern)
            if keys:
                await self.redis.delete(*keys)
            print(f"Cleared {len(keys)} cached responses")
        except Exception as e:
            print(f"Error clearing cache: {str(e)}")
            raise

    async def cleanup(self):
        """Cleanup resources."""
        if hasattr(self, 'redis'):
            await self.redis.aclose()