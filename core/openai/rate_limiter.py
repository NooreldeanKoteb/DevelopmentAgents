import asyncio
from datetime import datetime, timedelta
from core.config import get_settings, monitor_operation
import redis.asyncio as redis
from .errors import RateLimitError

class RateLimiter:
    """Implements rate limiting for OpenAI API calls."""

    def __init__(self):
        self.redis = redis.from_url(get_settings().REDIS_URL)
        self.settings = get_settings()
        # Configurable limits
        self.rpm_limit = self.settings.OPENAI_RPM_LIMIT
        self.tpm_limit = self.settings.OPENAI_TPM_LIMIT  # Tokens per minute
        self.retry_after = 5  # seconds
        
    @monitor_operation(agent_type="openai", operation="check_rate_limit")
    async def check_rate_limit(self, key: str, tokens: int = 0) -> bool:
        """Check both request and token rate limits."""
        current = datetime.utcnow()
        minute_window = current.strftime("%Y%m%d%H%M")
        
        # Keys for rate limiting
        rpm_key = f"ratelimit:rpm:{key}:{minute_window}"
        tpm_key = f"ratelimit:tpm:{key}:{minute_window}"
        
        async with self.redis.pipeline() as pipe:
            # Get current counts
            rpm_count = await self.redis.get(rpm_key) or 0
            tpm_count = await self.redis.get(tpm_key) or 0
            
            # Check limits
            if int(rpm_count) >= self.rpm_limit:
                raise RateLimitError(
                    message="Request rate limit exceeded",
                    retry_after=self.retry_after
                )
                
            if int(tpm_count) + tokens >= self.tpm_limit:
                raise RateLimitError(
                    message="Token rate limit exceeded",
                    retry_after=self.retry_after
                )
            
            # Update counters
            await pipe.incr(rpm_key)
            await pipe.expire(rpm_key, 60)
            
            if tokens > 0:
                await pipe.incrby(tpm_key, tokens)
                await pipe.expire(tpm_key, 60)
            
            await pipe.execute()
            
        return True
    
    async def wait_if_needed(self, key: str, tokens: int = 0) -> None:
        """Wait and retry if rate limited."""
        try:
            await self.check_rate_limit(key, tokens)
        except RateLimitError as e:
            await asyncio.sleep(e.retry_after)
            await self.wait_if_needed(key, tokens)