import pytest
from datetime import datetime
from core.messaging.message import Message

def test_message_creation():
    """Test basic message creation."""
    message = Message(
        id="test-1",
        type="test_type",
        content="test content",
        metadata={"recipient": "test-recipient"}
    )
    
    assert message.id == "test-1"
    assert message.type == "test_type"
    assert message.content == "test content"
    assert message.metadata == {"recipient": "test-recipient"}
    assert isinstance(message.timestamp, datetime)

def test_message_defaults():
    """Test message default values."""
    message = Message(
        type="test_type",
        content="test message"
    )
    
    assert isinstance(message.id, str)
    assert message.metadata == {}
    assert message.type == "test_type"
    assert message.content == "test message"
    assert isinstance(message.timestamp, datetime) 