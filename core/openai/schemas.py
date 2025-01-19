from typing import Dict, Any, Optional, Any
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict, field_serializer
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
    max_tokens: int = 4096

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
        extra='forbid',
    )

    content: Dict[str, Any]
    model: str
    usage: TokenUsage
    created_at: datetime = Field(default_factory=datetime.now)

    @field_serializer('*', when_used='json')
    def serialize_datetime(self, value: Any, _info) -> Any:
        if isinstance(value, datetime):
            return value.isoformat()
        return value
    
    def model_dump(self, **kwargs) -> Dict[str, Any]:
        """Override model_dump to handle datetime serialization."""
        data = super().model_dump(**kwargs)
        data['created_at'] = data['created_at'].isoformat()
        return data
    


class LLMConfig(BaseModel):
    """Configuration for LLM client."""
    model: str = "gpt-4-turbo-preview"
    temperature: float = 0.7
    max_tokens: Optional[int] = None
    top_p: float = 1.0
    frequency_penalty: float = 0.0
    presence_penalty: float = 0.0

    @classmethod
    def from_dict(cls, config: Dict[str, Any]) -> 'LLMConfig':
        """Create an LLMConfig instance from a dictionary."""
        return cls(**config)
