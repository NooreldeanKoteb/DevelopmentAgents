from typing import Dict, Any, Optional
import asyncio
import json
from openai import AsyncOpenAI, RateLimitError
from datetime import datetime
from pydantic import ValidationError

from core.config import get_settings, monitor_operation
from .schemas import OpenAIRequest, OpenAIResponse
from .cache import ResponseCache
from .rate_limiter import RateLimiter
from .usage import TokenUsageTracker
from .errors import (
    OpenAIError,
    RateLimitError,
    ResponseValidationError,
    TokenLimitError
)

class OpenAIClient:
    """Handles all OpenAI API communications with caching and rate limiting."""

    def __init__(self):
        self.settings = get_settings()
        self.client = AsyncOpenAI(api_key=self.settings.OPENAI_API_KEY)
        self.cache = ResponseCache()
        self.rate_limiter = RateLimiter()
        self.usage_tracker = TokenUsageTracker()
        self.total_tokens = 0
        self.total_cost = 0.0

    def _create_request(self, prompt: str, model: Optional[str], temperature: Optional[float], max_tokens: Optional[int], force_json: bool) -> OpenAIRequest:
        """Create a standardized request object."""
        # Add JSON formatting instruction if required
        full_prompt = f"{prompt}\nRespond only with valid JSON." if force_json else prompt
        
        return OpenAIRequest(
            model=model or self.settings.OPENAI_MODEL,
            prompt=full_prompt,
            temperature=temperature or self.settings.TEMPERATURE,
            max_tokens=max_tokens or self.settings.MAX_TOKENS
        )

    @monitor_operation(agent_type="openai", operation="completion")
    async def get_completion(
        self, 
        prompt: str, 
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        force_json: bool = True
    ) -> OpenAIResponse:
        """Get a completion from OpenAI with caching and rate limiting."""
        
        # Create standardized request
        request = self._create_request(prompt, model, temperature, max_tokens, force_json)
        
        # Generate cache key
        cache_key = request.cache_key

        # Debug logging
        print(f"Cache key: {cache_key}")
        print(f"Request params: {request.model_dump()}")

        # Check cache first
        cached_response = await self.cache.get(cache_key)
        if cached_response:
            print("Cache hit!")
            return OpenAIResponse.model_validate(cached_response)

        print("Cache miss - making API call")
        # Apply rate limiting
        await self.rate_limiter.acquire()

        try:
            # Make API call with retries
            response = await self._make_api_call_with_retry(request)

            # Parse and validate response
            parsed_response = self._parse_response(response)
            
            # Cache the response
            await self.cache.set(cache_key, parsed_response.model_dump())

            # Update usage metrics
            self._update_metrics(response)

            return parsed_response

        except Exception as e:
            raise OpenAIError(
                message=f"Error getting completion: {str(e)}",
                code="completion_error",
                details={"prompt": request.prompt}
            )

    async def _make_api_call_with_retry(
        self, 
        request: OpenAIRequest,
        max_retries: int = 3,
        base_delay: float = 1.0
    ) -> Dict[str, Any]:
        """Make API call with exponential backoff retry logic."""
        
        for attempt in range(max_retries):
            try:
                response = await self.client.chat.completions.create(
                    model=request.model,
                    messages=[{"role": "user", "content": request.prompt}],
                    temperature=request.temperature,
                    max_tokens=request.max_tokens,
                    response_format={"type": "json_object"}
                )
                return response

            except RateLimitError:
                if attempt == max_retries - 1:
                    raise
                delay = base_delay * (2 ** attempt)
                await asyncio.sleep(delay)

    def _parse_response(self, response: Dict[str, Any]) -> OpenAIResponse:
        """Parse and validate the OpenAI response."""
        try:
            content = response.choices[0].message.content
            # Ensure the response is valid JSON
            parsed_content = json.loads(content)
            
            return OpenAIResponse(
                content=parsed_content,
                model=response.model,
                usage=response.usage.model_dump(),
                created_at=datetime.fromtimestamp(response.created)
            )

        except (json.JSONDecodeError, ValidationError) as e:
            raise OpenAIError(
                message="Invalid response format",
                code="invalid_response",
                details={"error": str(e), "content": content}
            )

    def _update_metrics(self, response: Dict[str, Any]) -> None:
        """Update token usage and cost metrics."""
        usage = response.usage
        self.total_tokens += usage.total_tokens
        
        # Calculate cost based on model type
        model_rates = {
            "gpt-4": 0.03,      # $0.03 per 1K tokens
            "gpt-4-turbo": 0.01,  # $0.01 per 1K tokens
            "gpt-3.5-turbo": 0.002  # $0.002 per 1K tokens
        }
        
        model = response.model.split(':')[0]  # Handle model versions
        rate = model_rates.get(model, 0.01)  # Default rate if model not found
        
        # Calculate costs for input and output tokens separately
        input_cost = (usage.prompt_tokens / 1000) * rate
        output_cost = (usage.completion_tokens / 1000) * (rate * 2)  # Output typically costs 2x
        total_cost = input_cost + output_cost
        
        self.total_cost += total_cost
        
        # Update prometheus metrics if configured
        if hasattr(self, 'metrics'):
            self.metrics.token_usage.labels(model=model).inc(usage.total_tokens)
            self.metrics.cost_tracker.labels(model=model).inc(total_cost)