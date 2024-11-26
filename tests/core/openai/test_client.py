import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from datetime import datetime
from core.openai import OpenAIClient, OpenAIError, RateLimitError
from core.openai.schemas import OpenAIRequest, OpenAIResponse
import asyncio

@pytest.fixture
async def openai_client():
    """Fixture to provide a clean OpenAI client instance."""
    client = OpenAIClient()
    # Clear cache before test
    await client.cache.redis.flushdb()
    yield client
    # Clear cache after test
    await client.cache.redis.flushdb()
    await client.cache.redis.aclose()

@pytest.mark.asyncio
async def test_get_completion_success(openai_client):
    """Test successful completion request."""
    # Create a mock response object that matches the OpenAI API structure
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = '{"result": "test response"}'
    mock_response.model = "gpt-4"
    mock_response.usage.prompt_tokens = 10
    mock_response.usage.completion_tokens = 20
    mock_response.usage.total_tokens = 30
    mock_response.created = int(datetime.now().timestamp())
    mock_response.usage.model_dump = lambda: {
        "prompt_tokens": 10,
        "completion_tokens": 20,
        "total_tokens": 30
    }

    # Mock the create method
    with patch.object(openai_client.client.chat.completions, 'create', 
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
    # Create a mock response object
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = '{"result": "cached response"}'
    mock_response.model = "gpt-4"
    mock_response.usage.prompt_tokens = 10
    mock_response.usage.completion_tokens = 20
    mock_response.usage.total_tokens = 30
    mock_response.created = int(datetime.now().timestamp())
    mock_response.usage.model_dump = lambda: {
        "prompt_tokens": 10,
        "completion_tokens": 20,
        "total_tokens": 30
    }

    # Create identical requests to ensure same cache key
    prompt = "Test prompt"
    model = "gpt-4"
    temperature = 0.7
    max_tokens = 2000
    force_json = True

    with patch.object(openai_client.client.chat.completions, 'create', 
                     new_callable=AsyncMock) as mock_create:
        mock_create.return_value = mock_response
        
        # Clear cache before test
        await openai_client.cache.clear()
        
        # First call - should hit the API
        response1 = await openai_client.get_completion(
            prompt=prompt,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            force_json=force_json
        )
        
        # Verify cache was set
        request = openai_client._create_request(
            prompt=prompt,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            force_json=force_json
        )
        cache_key = request.cache_key
        
        # Add delay to ensure cache is set
        await asyncio.sleep(0.1)
        
        cached_data = await openai_client.cache.get(cache_key)
        assert cached_data is not None, "Response should be cached after first call"
        
        # Second call with identical parameters - should use cache
        response2 = await openai_client.get_completion(
            prompt=prompt,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            force_json=force_json
        )
        
        # Verify the API was only called once
        assert mock_create.call_count == 1, "API should only be called once due to caching"
        
        # Verify both responses are identical
        assert response1.content == response2.content
        assert response1.model == response2.model
        assert response1.usage.total_tokens == response2.usage.total_tokens

@pytest.mark.asyncio
async def test_get_completion_rate_limit(openai_client):
    """Test rate limit handling."""
    with patch.object(openai_client.client.chat.completions, 'create', 
                     new_callable=AsyncMock) as mock_create:
        mock_create.side_effect = RateLimitError()
        
        with pytest.raises(OpenAIError) as exc_info:
            await openai_client.get_completion("Test prompt")
        
        assert exc_info.value.code == "completion_error" 