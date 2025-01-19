"""Base schemas and shared utilities."""
from datetime import datetime
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field, ConfigDict
from uuid import uuid4

class BaseSchema(BaseModel):
    """Base schema with common functionality."""
    id: str = Field(default_factory=lambda: str(uuid4()), description="The unique identifier for the message")

class TimestampedSchema(BaseSchema):
    """Schema with timestamp fields."""
    created_at: datetime = Field(default_factory=datetime.now, description="creation timestamp")
    updated_at: Optional[datetime] = Field(default_factory=datetime.now, description="last update timestamp")
    completed_at: Optional[datetime] = Field(default=None, description="completion timestamp")

class MetadataSchema(BaseSchema):
    """Schema with metadata field."""
    metadata: Dict = Field(default_factory=dict, description="Additional metadata")

class DescriptiveSchema(BaseSchema):
    """Schema with metadata field."""
    name: str = Field(..., description="Name")
    description: str = Field(..., description="Description")

class ErrorSchema(BaseSchema):
    """Schema for error responses."""
    code: str
    message: str
    details: Optional[Dict[str, Any]] = None