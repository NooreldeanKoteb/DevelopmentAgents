"""Base schemas and shared utilities."""
from datetime import datetime
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field, ConfigDict

class BaseSchema(BaseModel):
    """Base schema with common fields."""
    id: str
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: Optional[datetime] = None
    metadata: Dict[str, Any] = Field(default_factory=dict) 

class TimestampedSchema(BaseModel):
    """Base schema with timestamps."""
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class MetadataSchema(BaseModel):
    """Base schema with metadata."""
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    metadata: Dict[str, Any] = Field(default_factory=dict) 