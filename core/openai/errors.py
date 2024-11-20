from typing import Optional, Dict, Any
from core.config.errors import AppError

class OpenAIError(Exception):
    """Base exception for OpenAI related errors."""
    def __init__(self, message: str, code: str, details: dict = None):
        self.message = message
        self.code = code
        self.details = details or {}
        super().__init__(self.message)

class RateLimitError(OpenAIError):
    """Raised when API rate limit is exceeded."""
    def __init__(self, message: str = "Rate limit exceeded", details: dict = None):
        super().__init__(message, code="rate_limit_error", details=details)

class TokenLimitError(OpenAIError):
    """Raised when token limit is exceeded."""
    def __init__(self, message: str = "Token limit exceeded", details: dict = None):
        super().__init__(message, code="token_limit_error", details=details)

class ResponseValidationError(OpenAIError):
    """Raised when response validation fails."""
    def __init__(self, message: str = "Response validation failed", details: dict = None):
        super().__init__(message, code="validation_error", details=details)

class APIConnectionError(OpenAIError):
    """API connection error."""
    def __init__(
        self,
        message: str,
        original
    ):
        super().__init__(message=message)
        self.original = original 