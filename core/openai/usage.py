from datetime import datetime
from typing import Dict, Any, Optional
import json
import redis.asyncio as redis
from core.config import get_settings, monitor_operation
from .errors import TokenLimitError

class TokenUsageTracker:
    def __init__(self):
        self.redis = redis.from_url(get_settings().REDIS_URL)
        self.settings = get_settings()
    
    @monitor_operation(agent_type="openai", operation="track_usage")
    async def track_usage(
        self,
        usage: Dict[str, int],
        model: str,
        cost: float,
        request_id: Optional[str] = None
    ) -> None:
        """Track token usage and cost."""
        timestamp = datetime.utcnow().isoformat()
        
        # Store detailed usage record
        usage_record = {
            "timestamp": timestamp,
            "model": model,
            "prompt_tokens": usage["prompt_tokens"],
            "completion_tokens": usage["completion_tokens"],
            "total_tokens": usage["total_tokens"],
            "cost": cost,
            "request_id": request_id
        }
        
        async with self.redis.pipeline() as pipe:
            # Store detailed record
            await pipe.lpush(
                "openai:usage:history",
                json.dumps(usage_record)
            )
            
            # Update running totals
            await pipe.hincrby("openai:usage:tokens", "total", usage["total_tokens"])
            await pipe.hincrby("openai:usage:tokens", "prompt", usage["prompt_tokens"])
            await pipe.hincrby("openai:usage:tokens", "completion", usage["completion_tokens"])
            
            # Update costs
            await pipe.hincrbyfloat("openai:usage:costs", "total", cost)
            await pipe.hincrbyfloat("openai:usage:costs", model, cost)
            
            await pipe.execute()
    
    async def get_usage_stats(self) -> Dict[str, Any]:
        """Get current usage statistics."""
        tokens = await self.redis.hgetall("openai:usage:tokens")
        costs = await self.redis.hgetall("openai:usage:costs")
        
        return {
            "tokens": tokens,
            "costs": costs
        } 