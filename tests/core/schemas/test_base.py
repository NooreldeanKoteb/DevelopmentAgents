import pytest
from datetime import datetime
from pydantic import ValidationError, ConfigDict
from core.schemas.base import (
    BaseSchema,
    TimestampedSchema,
    MetadataSchema,
    ErrorSchema
)

def test_base_schema():
    """Test BaseSchema functionality."""
    class TestSchema(BaseSchema):
        name: str
        value: int
        id: str = "test-id"

        model_config = ConfigDict(extra='forbid')

    # Test valid data
    data = TestSchema(name="test", value=1)
    assert data.name == "test"
    assert data.value == 1
    assert data.id == "test-id"

    # Test extra field rejection
    with pytest.raises(ValidationError):
        TestSchema(name="test", value=1, extra="invalid")

def test_timestamped_schema():
    """Test TimestampedSchema functionality."""
    class TestTimestamped(TimestampedSchema):
        name: str
        id: str = "test-id"

    # Test automatic timestamp generation
    data = TestTimestamped(name="test")
    assert isinstance(data.created_at, datetime)
    assert isinstance(data.updated_at, datetime)
    
    # Test custom timestamps
    now = datetime.now()
    data = TestTimestamped(
        name="test",
        created_at=now,
        updated_at=now
    )
    assert data.created_at == now
    assert data.updated_at == now

def test_metadata_schema():
    """Test MetadataSchema functionality."""
    class TestMetadata(MetadataSchema):
        name: str
        id: str = "test-id"

    # Test empty metadata
    data = TestMetadata(name="test")
    assert data.metadata == {}

    # Test with metadata
    data = TestMetadata(
        name="test",
        metadata={"key": "value"}
    )
    assert data.metadata == {"key": "value"}

def test_error_schema():
    """Test ErrorSchema functionality."""
    # Test minimal error
    error = ErrorSchema(
        code="test_error",
        message="Test error message"
    )
    assert error.code == "test_error"
    assert error.message == "Test error message"
    assert error.details is None

    # Test with details
    error = ErrorSchema(
        code="test_error",
        message="Test error message",
        details={"source": "test_case"}
    )
    assert error.details == {"source": "test_case"} 