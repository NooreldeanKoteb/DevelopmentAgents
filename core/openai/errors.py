from core.config.errors import AppError

class OpenAIError(AppError):
    """OpenAI specific errors."""
    pass

class RateLimitError(OpenAIError):
    """Rate limit exceeded errors."""
    pass

class ResponseValidationError(OpenAIError):
    """Response validation errors."""
    pass

class TokenLimitError(OpenAIError):
    """Token limit exceeded errors."""
    pass 