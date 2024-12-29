import pytest
from agents.director.action_analyzer import ActionAnalyzer
from agents.director.enums import ActionType
from agents.base.schemas import Message

@pytest.mark.asyncio
async def test_determine_action_type():
    """Test action type determination."""
    analyzer = ActionAnalyzer()
    
    create_message = Message(
        type="task_creation",
        content="create new task",
        metadata={}
    )
    assert await analyzer.determine_action_type(create_message) == "task_creation"
    
    update_message = Message(
        type="task_update",
        content="update task status",
        metadata={}
    )
    assert await analyzer.determine_action_type(update_message) == "task_update"