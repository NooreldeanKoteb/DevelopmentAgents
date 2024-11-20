import asyncio
from datetime import datetime, timedelta
from core.config import get_settings

class RateLimiter:
    """Implements rate limiting for API calls."""
    
    def __init__(self):
        self.settings = get_settings()
        self.calls = []
        self.lock = asyncio.Lock()
        
    async def acquire(self) -> None:
        """Acquire a rate limit token."""
        async with self.lock:
            now = datetime.now()
            window_start = now - timedelta(minutes=1)
            
            # Remove old calls
            self.calls = [t for t in self.calls if t > window_start]
            
            if len(self.calls) >= self.settings.RATE_LIMIT:
                # Wait until oldest call expires
                wait_time = (self.calls[0] - window_start).total_seconds()
                await asyncio.sleep(wait_time)
                
            self.calls.append(now)