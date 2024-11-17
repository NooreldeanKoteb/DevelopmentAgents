from typing import Optional, Dict, Any
import json
import redis.asyncio as redis
from datetime import timedelta
from core.config import get_settings, monitor_operation

class ResponseCache:
    """Handles caching of OpenAI responses in Redis."""

    def __init__(self):
        self.settings = get_settings()
        self.redis = redis.from_url(self.settings.REDIS_URL)
        self.ttl = 3600  # Cache for 1 hour by default

    async def get(self, key: str) -> Optional[Dict[str, Any]]:
        """Get cached response."""
        cached = await self.redis.get(f"openai:{key}")
        if cached:
            return json.loads(cached)
        return None

    async def set(self, key: str, value: Dict[str, Any]) -> None:
        """Cache response."""
        await self.redis.setex(
            f"openai:{key}",
            self.ttl,
            json.dumps(value)
        ) 