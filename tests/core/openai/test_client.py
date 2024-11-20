import pytest
from unittest.mock import AsyncMock, patch
from datetime import datetime
from core.openai import OpenAIClient, OpenAIError, RateLimitError
from core.openai.schemas import OpenAIRequest, OpenAIResponse

@pytest.fixture
async def openai_client():
    client = OpenAIClient()
    yield client
    # Cleanup
    await client.cache.redis.flushdb()

@pytest.mark.asyncio
async def test_get_completion_success(openai_client):
    """Test successful completion request."""
    mock_response = {
        "id": "test-id",
        "choices": [{
            "message": {
                "content": '{"result": "test response"}'
            }
        }],
        "model": "gpt-4",
        "usage": {
            "prompt_tokens": 10,
            "completion_tokens": 20,
            "total_tokens": 30
        },
        "created": int(datetime.now().timestamp())
    }

    with patch('openai.AsyncOpenAI.chat.completions.create', 
               new_callable=AsyncMock) as mock_create:
        mock_create.return_value = mock_response
        
        response = await openai_client.get_completion(
            prompt="Test prompt",
            model="gpt-4"
        )
        
        assert isinstance(response, OpenAIResponse)
        assert response.content == {"result": "test response"}
        assert response.model == "gpt-4"
        assert response.usage.total_tokens == 30

@pytest.mark.asyncio
async def test_get_completion_cache(openai_client):
    """Test completion caching."""
    mock_response = {
        "id": "test-id",
        "choices": [{
            "message": {
                "content": '{"result": "cached response"}'
            }
        }],
        "model": "gpt-4",
        "usage": {
            "prompt_tokens": 10,
            "completion_tokens": 20,
            "total_tokens": 30
        },
        "created": int(datetime.now().timestamp())
    }

    with patch('openai.AsyncOpenAI.chat.completions.create', 
               new_callable=AsyncMock) as mock_create:
        mock_create.return_value = mock_response
        
        # First call
        response1 = await openai_client.get_completion("Test prompt")
        
        # Second call should use cache
        response2 = await openai_client.get_completion("Test prompt")
        
        assert mock_create.call_count == 1
        assert response1.content == response2.content

@pytest.mark.asyncio
async def test_get_completion_rate_limit(openai_client):
    """Test rate limit handling."""
    with patch('openai.AsyncOpenAI.chat.completions.create', 
               new_callable=AsyncMock) as mock_create:
        mock_create.side_effect = RateLimitError()
        
        with pytest.raises(OpenAIError) as exc_info:
            await openai_client.get_completion("Test prompt")
        
        assert exc_info.value.code == "completion_error" 