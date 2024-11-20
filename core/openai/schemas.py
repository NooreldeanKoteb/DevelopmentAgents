from typing import Dict, Any, Optional
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict
import hashlib
import json

class OpenAIRequest(BaseModel):
    """Schema for OpenAI API requests."""
    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        validate_assignment=True,
        extra='forbid'
    )

    model: str
    prompt: str
    temperature: float = 0.7
    max_tokens: int = 2000

    @property
    def cache_key(self) -> str:
        """Generate a unique cache key for this request."""
        request_dict = self.model_dump()
        serialized = json.dumps(request_dict, sort_keys=True)
        return hashlib.sha256(serialized.encode()).hexdigest()

class TokenUsage(BaseModel):
    """Schema for token usage tracking."""
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int

class OpenAIResponse(BaseModel):
    """Schema for OpenAI API responses."""
    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        validate_assignment=True,
        extra='forbid'
    )

    content: Dict[str, Any]
    model: str
    usage: TokenUsage
    created_at: datetime = Field(default_factory=datetime.now) 