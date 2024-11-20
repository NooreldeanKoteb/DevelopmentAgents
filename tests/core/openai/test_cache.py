import pytest
import json
from core.openai.cache import ResponseCache

@pytest.mark.asyncio
async def test_cache_operations():
    """Test basic cache operations."""
    cache = ResponseCache()
    
    test_data = {"test": "data"}
    test_key = "test_key"
    
    # Test set
    await cache.set(test_key, test_data)
    
    # Test get
    result = await cache.get(test_key)
    assert result == test_data
    
    # Test TTL
    ttl = await cache.redis.ttl(f"openai:cache:{test_key}")
    assert ttl > 0

@pytest.mark.asyncio
async def test_cache_missing():
    """Test cache miss handling."""
    cache = ResponseCache()
    
    result = await cache.get("nonexistent")
    assert result is None 