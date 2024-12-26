

# Core OpenAI Integration Documentation

## Overview
The OpenAI integration system provides a robust interface for interacting with OpenAI's APIs, handling authentication, rate limiting, retries, and response processing. It's designed to support various AI operations including completions, embeddings, and function calling.

## Key Components

### 1. OpenAI Client
**Location**: `core/openai/client.py`

Main interface for OpenAI API interactions.

**Key Features**:
- API key management
- Rate limiting
- Retry logic
- Response caching
- Error handling
- Async support

**Usage Example**:
```python
from core.openai import OpenAIClient

client = OpenAIClient()
response = await client.complete(
    prompt="Explain Python async/await",
    model="gpt-4",
    max_tokens=500
)
```

### 2. Models Configuration
**Location**: `core/openai/models.py`

Defines available models and their configurations.

**Example Configuration**:
```python
OPENAI_MODELS = {
    "gpt-4": {
        "max_tokens": 8192,
        "temperature_range": (0.0, 2.0),
        "default_temperature": 0.7,
        "cost_per_1k_tokens": 0.03,
    },
    "gpt-3.5-turbo": {
        "max_tokens": 4096,
        "temperature_range": (0.0, 2.0),
        "default_temperature": 0.7,
        "cost_per_1k_tokens": 0.002,
    }
}
```

### 3. Rate Limiter
**Location**: `core/openai/rate_limiter.py`

Manages API request rates and quotas.

**Key Features**:
- Request throttling
- Token counting
- Cost tracking
- Quota management
- Concurrent request limiting

## Common Operations

### 1. Text Completion
```python
async def get_completion(prompt: str) -> str:
    client = OpenAIClient()
    response = await client.complete(
        prompt=prompt,
        model="gpt-4",
        temperature=0.7,
        max_tokens=1000
    )
    return response.choices[0].text
```

### 2. Chat Completion
```python
async def chat_completion(messages: List[Dict[str, str]]) -> str:
    client = OpenAIClient()
    response = await client.chat_complete(
        messages=messages,
        model="gpt-4",
        temperature=0.7
    )
    return response.choices[0].message.content
```

### 3. Embeddings
```python
async def get_embedding(text: str) -> List[float]:
    client = OpenAIClient()
    response = await client.create_embedding(
        input=text,
        model="text-embedding-3-large"
    )
    return response.data[0].embedding
```

## Error Handling

Custom error types:
```python
class OpenAIError(Exception):
    """Base class for OpenAI-related errors"""
    pass

class RateLimitError(OpenAIError):
    """Raised when rate limits are exceeded"""
    pass

class TokenLimitError(OpenAIError):
    """Raised when token limits are exceeded"""
    pass

class APIError(OpenAIError):
    """Raised for API-related errors"""
    pass
```

## Best Practices

1. **Error Handling**:
```python
try:
    response = await client.complete(prompt)
except RateLimitError:
    await asyncio.sleep(60)  # Wait and retry
except TokenLimitError:
    # Split prompt and try again
    responses = await process_long_prompt(prompt)
except APIError as e:
    logger.error(f"OpenAI API error: {e}")
```

2. **Cost Management**:
```python
async def track_api_costs():
    costs = await client.get_usage_costs()
    if costs.total > DAILY_BUDGET:
        await notify_admin("Daily API budget exceeded")
```

3. **Response Caching**:
```python
@cached(ttl=3600)  # Cache for 1 hour
async def get_cached_completion(prompt: str) -> str:
    return await client.complete(prompt)
```

## Configuration

```python
OPENAI_CONFIG = {
    "api_key": "your-api-key",
    "organization": "your-org-id",
    "default_model": "gpt-4",
    "max_retries": 3,
    "timeout": 30,
    "rate_limits": {
        "requests_per_minute": 60,
        "tokens_per_minute": 90000
    }
}
```

## Monitoring Integration

1. **Metrics Tracking**:
```python
@metrics.track_openai_request
async def monitored_completion(prompt: str):
    start_time = time.time()
    try:
        response = await client.complete(prompt)
        metrics.observe(
            "openai_request_duration",
            time.time() - start_time
        )
        return response
    except Exception as e:
        metrics.increment("openai_errors_total")
        raise
```

2. **Usage Logging**:
```python
async def log_api_usage(response):
    logger.info("OpenAI API call completed", extra={
        "tokens_used": response.usage.total_tokens,
        "model": response.model,
        "cost": calculate_cost(response)
    })
```

## Performance Optimization

1. **Batch Processing**:
```python
async def batch_process_prompts(prompts: List[str]):
    return await client.batch_complete(
        prompts,
        batch_size=5,
        concurrent_requests=3
    )
```

2. **Token Management**:
```python
def optimize_prompt(prompt: str, max_tokens: int) -> str:
    tokens = count_tokens(prompt)
    if tokens > max_tokens:
        return truncate_prompt(prompt, max_tokens)
    return prompt
```

## Testing

Example test cases:
```python
async def test_openai_client():
    client = OpenAIClient()
    
    # Test completion
    response = await client.complete("Test prompt")
    assert response.choices[0].text
    
    # Test rate limiting
    responses = await asyncio.gather(
        *[client.complete("Test") for _ in range(10)]
    )
    assert len(responses) == 10
    
    # Test error handling
    with pytest.raises(TokenLimitError):
        await client.complete("x" * 10000)
```

## Common Use Cases

1. **Content Generation**:
```python
async def generate_content(topic: str) -> str:
    prompt = load_prompt_template("content_generation")
    return await client.complete(
        prompt.format(topic=topic),
        temperature=0.8
    )
```

2. **Text Analysis**:
```python
async def analyze_sentiment(text: str) -> Dict[str, float]:
    response = await client.complete(
        prompt=f"Analyze sentiment: {text}",
        temperature=0.0  # Deterministic
    )
    return parse_sentiment_response(response)
```

3. **Code Generation**:
```python
async def generate_code(specification: str) -> str:
    return await client.complete(
        prompt=f"Generate code: {specification}",
        model="gpt-4",
        temperature=0.2,
        stop=["```"]
    )
```

## Development Guidelines

1. Always handle API errors gracefully
2. Implement proper rate limiting
3. Monitor API usage and costs
4. Cache responses when appropriate
5. Use appropriate models for tasks
6. Implement retry logic
7. Maintain proper logging
8. Track performance metrics

For more detailed examples and advanced usage patterns, refer to the tests in `tests/core/openai/`.
