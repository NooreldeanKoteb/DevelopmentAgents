import pytest
from core.messaging import MessageBroker, Message
import asyncio

@pytest.mark.asyncio
async def test_publish_subscribe():
    """Test basic publish/subscribe functionality."""
    broker = MessageBroker()
    received_messages = []
    
    async def callback(message: Message):
        received_messages.append(message)
    
    # Subscribe to topic
    await broker.subscribe("test.topic", callback)
    
    # Publish message
    message = Message(
        topic="test.topic",
        content={"key": "value"},
        sender="test_sender"
    )
    await broker.publish(message)
    
    # Allow time for async processing
    await asyncio.sleep(0.1)
    
    assert len(received_messages) == 1
    assert received_messages[0].id == message.id

@pytest.mark.asyncio
async def test_multiple_subscribers():
    """Test multiple subscribers for the same topic."""
    broker = MessageBroker()
    received_1 = []
    received_2 = []
    
    async def callback_1(message: Message):
        received_1.append(message)
        
    async def callback_2(message: Message):
        received_2.append(message)
    
    await broker.subscribe("test.topic", callback_1)
    await broker.subscribe("test.topic", callback_2)
    
    message = Message(
        topic="test.topic",
        content={"key": "value"},
        sender="test_sender"
    )
    await broker.publish(message)
    
    await asyncio.sleep(0.1)
    
    assert len(received_1) == 1
    assert len(received_2) == 1

@pytest.mark.asyncio
async def test_unsubscribe():
    """Test unsubscribe functionality."""
    broker = MessageBroker()
    received_messages = []
    
    async def callback(message: Message):
        received_messages.append(message)
    
    # Subscribe and then unsubscribe
    await broker.subscribe("test.topic", callback)
    await broker.unsubscribe("test.topic", callback)
    
    message = Message(
        topic="test.topic",
        content={"key": "value"},
        sender="test_sender"
    )
    await broker.publish(message)
    
    await asyncio.sleep(0.1)
    
    assert len(received_messages) == 0

@pytest.mark.asyncio
async def test_get_message():
    """Test getting messages from queue."""
    broker = MessageBroker()
    
    message = Message(
        topic="test.topic",
        content={"key": "value"},
        sender="test_sender"
    )
    await broker.publish(message)
    
    retrieved = await broker.get_message("test.topic")
    assert retrieved is not None
    assert retrieved.id == message.id
    
    # Queue should be empty now
    empty_message = await broker.get_message("test.topic")
    assert empty_message is None 