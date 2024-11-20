import pytest
import asyncio
from core.messaging import MessageQueue, Message

@pytest.mark.asyncio
async def test_queue_operations():
    """Test basic queue operations."""
    queue = MessageQueue()
    
    message = Message(
        topic="test.topic",
        content={"key": "value"},
        sender="test_sender"
    )
    
    # Test put and get
    await queue.put(message)
    retrieved = await queue.get()
    
    assert retrieved.id == message.id
    assert retrieved.content == message.content

@pytest.mark.asyncio
async def test_queue_timeout():
    """Test queue timeout behavior."""
    queue = MessageQueue()
    
    # Test get with timeout
    result = await queue.get(timeout=0.1)
    assert result is None

@pytest.mark.asyncio
async def test_queue_size():
    """Test queue size operations."""
    queue = MessageQueue(maxsize=2)
    
    message1 = Message(topic="test", content={"id": 1}, sender="test")
    message2 = Message(topic="test", content={"id": 2}, sender="test")
    
    assert queue.empty()
    assert queue.qsize() == 0
    
    await queue.put(message1)
    await queue.put(message2)
    
    assert not queue.empty()
    assert queue.qsize() == 2 