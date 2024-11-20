import pytest
from datetime import datetime, timedelta
from core.openai.rate_limiter import RateLimiter

@pytest.mark.asyncio
async def test_rate_limiter_basic():
    """Test basic rate limiting."""
    limiter = RateLimiter()
    
    # Should acquire without waiting
    start_time = datetime.now()
    await limiter.acquire()
    duration = datetime.now() - start_time
    
    assert duration.total_seconds() < 0.1

@pytest.mark.asyncio
async def test_rate_limiter_limit():
    """Test rate limiter when limit is reached."""
    limiter = RateLimiter()
    
    # Fill up the rate limit
    for _ in range(limiter.settings.RATE_LIMIT):
        await limiter.acquire()
    
    # Next acquire should wait
    start_time = datetime.now()
    await limiter.acquire()
    duration = datetime.now() - start_time
    
    assert duration.total_seconds() >= 1.0 