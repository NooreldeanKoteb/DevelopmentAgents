import pytest
from datetime import datetime, timedelta
from core.storage.message_store import MessageStore
from core.messaging import Message
import asyncio

@pytest.fixture
async def message_store(redis_client):
    """Create a message store instance."""
    return MessageStore(redis=redis_client)

@pytest.mark.asyncio
async def test_store_and_retrieve_message(message_store):
    """Test storing and retrieving messages."""
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
    
    # Store messages
    for msg in messages:
        await message_store.store_message(msg)
        # Add small delay to ensure distinct timestamps
        await asyncio.sleep(0.1)
    
    # Get messages from last 2 minutes
    recent_messages = await message_store.get_messages(
        "test_topic",
        start_time=now - timedelta(minutes=2)
    )
    
    # Should get exactly 3 messages (0, 1, and 2 minutes ago)
    assert len(recent_messages) == 3
    
    # Verify messages are in chronological order (newest first)
    timestamps = [msg.timestamp for msg in recent_messages]
    assert all(timestamps[i] >= timestamps[i+1] for i in range(len(timestamps)-1))