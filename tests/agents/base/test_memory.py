import pytest
import asyncio
from datetime import timedelta
import json
from agents.base import AgentMemory, MemoryError


@pytest.fixture
async def memory():
    """Provide a memory instance."""
    memory = AgentMemory("test-agent")
    yield memory
    await memory.clear()

@pytest.mark.asyncio
async def test_memory_storage(memory):
    """Test basic memory storage and retrieval."""
    test_data = {"key": "value"}
    
    # Store data
    await memory.store("test_key", test_data)
    
    # Retrieve data
    retrieved = await memory.retrieve("test_key")
    assert retrieved == test_data

@pytest.mark.asyncio
async def test_memory_ttl(memory):
    """Test memory TTL functionality."""
    try:
        # Store data with short TTL
        await memory.store(
            "ttl_test",
            "test_data",
            ttl=timedelta(seconds=1)
        )
        
        # Verify data exists
        assert await memory.retrieve("ttl_test") == "test_data"
        
        # Wait for expiration
        await asyncio.sleep(1.1)
        
        # Verify data is expired
        assert await memory.retrieve("ttl_test") is None
        
    except asyncio.CancelledError:
        # Ensure cleanup if test is cancelled during sleep
        await memory.clear("ttl_test")
        raise

@pytest.mark.asyncio
async def test_memory_listing(memory):
    """Test memory listing functionality."""
    # Store multiple items
    test_data = {
        "key1": "value1",
        "key2": "value2",
        "other": "value3"
    }
    
    for key, value in test_data.items():
        await memory.store(key, value)
    
    # List memories with pattern
    memories = await memory.list_memories("key*")
    assert len(memories) == 2
    assert all(m["key"].startswith("key") for m in memories)

@pytest.mark.asyncio
async def test_memory_clear(memory):
    """Test memory clearing."""
    # Store data
    await memory.store("test1", "value1")
    await memory.store("test2", "value2")
    
    # Clear specific pattern
    await memory.clear("test1")
    assert await memory.retrieve("test1") is None
    assert await memory.retrieve("test2") is not None
    
    # Clear all
    await memory.clear()
    assert await memory.retrieve("test2") is None

@pytest.mark.asyncio
async def test_memory_concurrent_access(memory):
    """Test concurrent memory access."""
    async def store_and_retrieve(key: str, value: str):
        await memory.store(key, value)
        retrieved = await memory.retrieve(key)
        assert retrieved == value
    
    # Create multiple concurrent operations
    tasks = [
        store_and_retrieve(f"key{i}", f"value{i}")
        for i in range(5)
    ]
    
    # Run concurrently
    await asyncio.gather(*tasks)

@pytest.mark.asyncio
async def test_memory_error_handling(memory):
    """Test error handling in memory operations."""
    with pytest.raises(MemoryError):
        await memory.retrieve("nonexistent_key", raise_error=True) 