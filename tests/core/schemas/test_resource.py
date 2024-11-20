import pytest
from pydantic import ValidationError
from core.schemas.resource import (
    ResourceSchema,
    ResourceType,
    ResourceStatus
)

def test_resource_schema():
    """Test ResourceSchema validation and defaults."""
    # Test minimal resource
    resource = ResourceSchema(
        id="test-resource",
        name="Test Resource",
        type=ResourceType.CPU
    )
    assert resource.id == "test-resource"
    assert resource.name == "Test Resource"
    assert resource.type == ResourceType.CPU
    assert resource.status == ResourceStatus.AVAILABLE
    assert resource.capacity == 1.0
    assert resource.current_usage == 0.0

    # Test full resource configuration
    resource = ResourceSchema(
        id="test-resource",
        name="Test Resource",
        type=ResourceType.MEMORY,
        status=ResourceStatus.IN_USE,
        capacity=16.0,
        current_usage=8.0,
        limits={"max_usage": 14.0},
        allocated_to="agent-123"
    )
    assert resource.status == ResourceStatus.IN_USE
    assert resource.capacity == 16.0
    assert resource.current_usage == 8.0
    assert resource.limits["max_usage"] == 14.0
    assert resource.allocated_to == "agent-123"

def test_resource_validation():
    """Test resource validation rules."""
    # Test invalid usage
    with pytest.raises(ValidationError):
        ResourceSchema(
            id="test-resource",
            name="Test Resource",
            type=ResourceType.CPU,
            current_usage=2.0,
            capacity=1.0
        ) 