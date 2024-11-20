import pytest
from datetime import datetime
from agents.base import AgentContext
from core.messaging import Message

@pytest.fixture
def context():
    """Provide a context instance."""
    return AgentContext()

def test_context_update(context):
    """Test context update with messages."""
    message = Message(
        topic="test",
        content={"test": "data"},
        sender="test"
    )
    
    context.update(message)
    assert len(context.history) == 1
    assert context.history[0]["message"] == message

def test_context_history(context):
    """Test conversation history management."""
    # Add messages
    messages = [
        Message(topic="test1", content={"i": i}, sender="test")
        for i in range(3)
    ]
    
    for msg in messages:
        context.update(msg)
    
    # Get history
    history = context.get_history(limit=2)
    assert len(history) == 2
    
    # Get history by topic
    topic_history = context.get_history(topic="test1")
    assert len(topic_history) == 3

def test_context_variables(context):
    """Test context variables."""
    context.set_variable("test_var", "test_value")
    assert context.get_variable("test_var") == "test_value"
    
    # Test non-existent variable
    assert context.get_variable("nonexistent") is None

def test_context_clear(context):
    """Test context clearing."""
    # Add data
    context.update(Message(
        topic="test",
        content={},
        sender="test"
    ))
    context.set_variable("test", "value")
    
    # Clear context
    context.clear()
    assert len(context.history) == 0
    assert len(context.variables) == 0

def test_context_max_history(context):
    """Test maximum history limit."""
    context = AgentContext(max_history=2)
    
    # Add messages
    for i in range(3):
        context.update(Message(
            topic="test",
            content={"i": i},
            sender="test"
        ))
    
    assert len(context.history) == 2
    assert context.get_history()[0]["message"].content["i"] == 1 