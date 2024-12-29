import pytest
from agents.director.action_analyzer import ActionAnalyzer
from agents.director.enums import ActionType
from core.messaging.message import Message
@pytest.mark.asyncio
@pytest.mark.parametrize("content,expected_type", [
    ("create new task", "task_creation"),
    ("update task status", "task_update"),
    ("allocate resources", "resource_allocation"),
    ("error in task", "error_handling"),
    ("random message", "project_update"),
])
async def test_action_analyzer_patterns(content, expected_type):
    """Test action analyzer pattern matching."""
    analyzer = ActionAnalyzer()
    message = Message(
        id="test-1",
        type="default",
        content=content
    )
    
    action_type = await analyzer.determine_action_type(message)
    assert action_type == expected_type

@pytest.mark.asyncio
async def test_action_analyzer_metadata_override():
    """Test that metadata can override pattern matching."""
    analyzer = ActionAnalyzer()
    message = Message(
        id="test-1",
        type="default",
        content="create new task",
        metadata={"action_type": "priority_adjustment"}
    )
    
    action_type = await analyzer.determine_action_type(message)
    assert action_type == "priority_adjustment" 