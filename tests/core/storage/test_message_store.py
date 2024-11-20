import pytest
from datetime import datetime, timedelta
from core.storage.message_store import MessageStore
from core.messaging import Message

@pytest.fixture
async def message_store():
    store = MessageStore()
    yield store
    # Cleanup after tests
    await store.redis.flushdb()

@pytest.mark.asyncio
async def test_store_and_retrieve_message(message_store):
    """Test basic message storage and retrieval."""
    message = Message(
        topic="test_topic",
        content={"test": "data"},
        sender="test_sender"
    )
    
    await message_store.store_message(message)
    
    messages = await message_store.get_messages("test_topic")
    assert len(messages) == 1
    assert messages[0].id == message.id
    assert messages[0].content == message.content

@pytest.mark.asyncio
async def test_message_time_range(message_store):
    """Test retrieving messages by time range."""
    # Create messages with different timestamps
    now = datetime.now()
    
    messages = [
        Message(
            topic="test_topic",
            content={"index": i},
            sender="test_sender",
            timestamp=now - timedelta(minutes=i)
        )
        for i in range(5)
    ]
    
    for msg in messages:
        await message_store.store_message(msg)
    
    # Get messages from last 2 minutes
    recent_messages = await message_store.get_messages(
        "test_topic",
        start_time=now - timedelta(minutes=2)
    )
    
    assert len(recent_messages) == 2
    assert recent_messages[0].timestamp >= now - timedelta(minutes=2)
    assert recent_messages[1].timestamp >= now - timedelta(minutes=2)