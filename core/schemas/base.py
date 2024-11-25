"""Base schemas and shared utilities."""
from datetime import datetime
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field, ConfigDict

class BaseSchema(BaseModel):
    """Base schema with common functionality."""
    id: str = Field(..., description="Unique identifier")

class TimestampedSchema(BaseSchema):
    """Schema with timestamp fields."""
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

class MetadataSchema(BaseSchema):
    """Schema with metadata field."""
    metadata: Dict[str, Any] = Field(default_factory=dict)

class ErrorSchema(BaseModel):
    """Schema for error responses."""
    code: str
    message: str
    details: Optional[Dict[str, Any]] = None