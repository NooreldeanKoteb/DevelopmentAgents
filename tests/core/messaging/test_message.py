import pytest
from datetime import datetime
from core.messaging import Message

def test_message_creation():
    """Test basic message creation and validation."""
    message = Message(
        topic="test.topic",
        content={"key": "value"},
        sender="test_sender"
    )
    
    assert message.topic == "test.topic"
    assert message.content == {"key": "value"}
    assert message.sender == "test_sender"
    assert message.id is not None
    assert isinstance(message.timestamp, datetime)
    assert message.recipient is None
    assert message.correlation_id is None
    assert message.reply_to is None
    assert message.metadata == {}

def test_message_with_optional_fields():
    """Test message creation with all optional fields."""
    message = Message(
        topic="test.topic",
        content={"key": "value"},
        sender="test_sender",
        recipient="test_recipient",
        correlation_id="corr-123",
        reply_to="reply.topic",
        metadata={"priority": "high"}
    )
    
    assert message.recipient == "test_recipient"
    assert message.correlation_id == "corr-123"
    assert message.reply_to == "reply.topic"
    assert message.metadata == {"priority": "high"} 