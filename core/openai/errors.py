from typing import Optional, Dict, Any
from core.config.errors import AppError

class OpenAIError(AppError):
    """Base OpenAI error."""
    pass

class RateLimitError(OpenAIError):
    """Rate limit exceeded error."""
    def __init__(
        self,
        message: str,
        retry_after: int,
        code: str = "rate_limit_exceeded"
    ):
        super().__init__(message=message, code=code)
        self.retry_after = retry_after

class TokenLimitError(OpenAIError):
    """Token usage limit exceeded error."""
    def __init__(
        self,
        message: str,
        current_usage: int,
        limit: int,
        code: str = "token_limit_exceeded"
    ):
        super().__init__(message=message, code=code)
        self.current_usage = current_usage
        self.limit = limit

class ResponseValidationError(OpenAIError):
    """Response validation error."""
    def __init__(
        self,
        message: str,
        response: Dict[str, Any],
        code: str = "invalid_response"
    ):
        super().__init__(message=message, code=code)
        self.response = response

class APIConnectionError(OpenAIError):
    """API connection error."""
    def __init__(
        self,
        message: str,
        original
    ):
        super().__init__(message=message)
        self.original = original 