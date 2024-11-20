from typing import Optional, Dict, Any
import json
from datetime import datetime, timedelta
import redis.asyncio as aioredis
from core.config import get_settings

class ResponseCache:
    """Caches OpenAI responses to reduce API calls."""
    
    def __init__(self):
        self.settings = get_settings()
        self.redis = aioredis.from_url(
            self.settings.REDIS_URL,
            decode_responses=True
        )
        self.ttl = timedelta(hours=24)
        
    async def get(self, key: str) -> Optional[Dict[str, Any]]:
        """Get cached response."""
        try:
            data = await self.redis.get(f"openai:cache:{key}")
            return json.loads(data) if data else None
        except Exception:
            return None
            
    async def set(self, key: str, value: Dict[str, Any]) -> None:
        """Cache a response."""
        try:
            await self.redis.setex(
                f"openai:cache:{key}",
                self.ttl,
                json.dumps(value)
            )
        except Exception:
            pass  # Fail silently on cache errors 