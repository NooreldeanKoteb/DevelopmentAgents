import pytest
import asyncio
from core.messaging.broker import MessageBroker
from core.messaging.message import Message

@pytest.fixture
async def broker():
    """Provide a message broker instance."""
    broker = MessageBroker()
    yield broker
    # Cleanup
    await broker.close()  # Make sure we have a close method to cleanup resources

@pytest.mark.asyncio
async def test_broker_publish_subscribe():
    """Test basic publish/subscribe functionality."""
    broker = MessageBroker()
    
    # Use asyncio.Queue for receiving messages
    received_messages = asyncio.Queue()
    
    async def message_handler(message):
        await received_messages.put(message)
    
    # Subscribe with timeout
    await broker.subscribe("test_topic", message_handler)
    
    # Publish test message
    test_message = Message(
        topic="test_topic",
        content={"test": "data"},
        sender="test_sender"
    )
    await broker.publish(test_message)
    
    # Wait for message with timeout
    try:
        received = await asyncio.wait_for(received_messages.get(), timeout=1.0)
        assert received == test_message
    except asyncio.TimeoutError:
        pytest.fail("Message not received within timeout")
    finally:
        await broker.close()

@pytest.mark.asyncio
async def test_broker_multiple_subscribers():
    """Test multiple subscribers receiving messages."""
    broker = MessageBroker()
    
    received_messages = []
    event = asyncio.Event()
    
    async def message_handler1(message):
        received_messages.append(("handler1", message))
        if len(received_messages) == 2:
            event.set()
            
    async def message_handler2(message):
        received_messages.append(("handler2", message))
        if len(received_messages) == 2:
            event.set()
    
    # Subscribe both handlers
    await broker.subscribe("test_topic", message_handler1)
    await broker.subscribe("test_topic", message_handler2)
    
    # Publish test message
    test_message = Message(
        topic="test_topic",
        content={"test": "data"},
        sender="test_sender"
    )
    await broker.publish(test_message)
    
    # Wait for both handlers with timeout
    try:
        await asyncio.wait_for(event.wait(), timeout=1.0)
        assert len(received_messages) == 2
        assert any(h == "handler1" for h, _ in received_messages)
        assert any(h == "handler2" for h, _ in received_messages)
    except asyncio.TimeoutError:
        pytest.fail("Not all messages received within timeout")
    finally:
        await broker.close()

@pytest.mark.asyncio
async def test_broker_unsubscribe():
    """Test unsubscribing from topics."""
    broker = MessageBroker()
    received_messages = asyncio.Queue()
    
    async def message_handler(message):
        await received_messages.put(message)
    
    # Subscribe and then unsubscribe
    await broker.subscribe("test_topic", message_handler)
    await broker.unsubscribe("test_topic", message_handler)
    
    # Publish test message
    test_message = Message(
        topic="test_topic",
        content={"test": "data"},
        sender="test_sender"
    )
    await broker.publish(test_message)
    
    # Verify no message received
    try:
        with pytest.raises(asyncio.TimeoutError):
            await asyncio.wait_for(received_messages.get(), timeout=0.1)
    finally:
        await broker.close()

@pytest.mark.asyncio
async def test_broker_error_handling():
    """Test broker error handling."""
    broker = MessageBroker()
    error_received = asyncio.Event()
    
    async def failing_handler(message):
        raise Exception("Test error")
    
    async def error_handler(error):
        assert isinstance(error, Exception)
        assert str(error) == "Test error"
        error_received.set()
    
    broker.on_error(error_handler)
    await broker.subscribe("test_topic", failing_handler)
    
    # Publish test message
    test_message = Message(
        topic="test_topic",
        content={"test": "data"},
        sender="test_sender"
    )
    await broker.publish(test_message)
    
    # Wait for error handling with increased timeout
    try:
        await asyncio.wait_for(error_received.wait(), timeout=2.0)
        assert error_received.is_set()
    except asyncio.TimeoutError:
        pytest.fail("Error not handled within timeout")
    
    # Ensure cleanup
    await broker.cleanup() 