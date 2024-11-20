import pytest
from agents.base.base_agent import BaseAgent
from agents.base.message import Message

@pytest.mark.asyncio
async def test_base_agent_abstract_methods():
    """Test that base agent methods raise NotImplementedError."""
    agent = BaseAgent()
    
    with pytest.raises(NotImplementedError):
        await agent.process_message(Message(id="1", content="test"))
        
    with pytest.raises(NotImplementedError):
        await agent.handle_error(Exception("test")) 

def test_base_agent_abstract_methods():
    """Test that BaseAgent cannot be instantiated directly."""
    class TestAgent(BaseAgent):
        pass  # Missing required abstract methods
        
    with pytest.raises(TypeError, match="Can't instantiate abstract class TestAgent"):
        TestAgent()