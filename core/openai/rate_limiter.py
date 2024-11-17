import asyncio
from datetime import datetime, timedelta
from core.config import get_settings

class RateLimiter:
    """Implements rate limiting for OpenAI API calls."""

    def __init__(self):
        self.settings = get_settings()
        self.requests = []
        self.lock = asyncio.Lock()

    async def acquire(self) -> None:
        """Acquire a rate limit token."""
        async with self.lock:
            now = datetime.now()
            window_start = now - timedelta(seconds=self.settings.RATE_LIMIT_PERIOD)
            
            # Remove old requests
            self.requests = [t for t in self.requests if t > window_start]
            
            # If at limit, wait until we can make another request
            if len(self.requests) >= self.settings.RATE_LIMIT_REQUESTS:
                wait_time = (self.requests[0] - window_start).total_seconds()
                await asyncio.sleep(wait_time)
                
            # Add current request
            self.requests.append(now) 