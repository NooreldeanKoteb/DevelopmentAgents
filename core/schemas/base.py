"""Base schemas and shared utilities."""
from datetime import datetime
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field, ConfigDict

class BaseSchema(BaseModel):
    """Base schema with common functionality."""
    id: str = Field(..., description="Unique identifier")

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

class ErrorSchema(BaseModel):
    """Schema for error responses."""
    code: str
    message: str
    details: Optional[Dict[str, Any]] = None