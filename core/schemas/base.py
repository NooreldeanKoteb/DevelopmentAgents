from typing import Dict, Any, Optional, Type, Union
from enum import Enum
from datetime import datetime
from pydantic import BaseModel, Field, ValidationError, ConfigDict
from uuid import UUID, uuid4

class SchemaVersion(str, Enum):
    """Schema version enumeration."""
    V1 = "1.0"
    V1_1 = "1.1"
    V2 = "2.0"

class BaseSchema(BaseModel):
    """Base schema with versioning support."""
    schema_version: SchemaVersion = Field(default=SchemaVersion.V2)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    id: UUID = Field(default_factory=uuid4)
    
    model_config = ConfigDict(
        json_encoders={
            datetime: lambda v: v.isoformat(),
            UUID: str
        }
    )

class ValidationResult(BaseModel):
    """Schema validation result."""
    is_valid: bool
    errors: Optional[Dict[str, Any]] = None
    transformed_data: Optional[Dict[str, Any]] = None
    original_data: Dict[str, Any]
    schema_version: SchemaVersion 