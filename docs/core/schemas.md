

# Core Schema System Documentation

## Overview
The schema system provides data validation, serialization, and documentation for all data structures in the application. Built on Pydantic, it ensures type safety and data consistency across the system.

## Key Components

### 1. Base Schemas
**Location**: `core/schemas/base.py`

Base schema classes that other schemas inherit from.

**Key Features**:
- Common validation rules
- Base field definitions
- Versioning support
- Serialization methods
- Metadata handling

```python
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, Dict, Any

class BaseSchema(BaseModel):
    id: str = Field(default_factory=uuid4)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
```

### 2. Message Schemas
**Location**: `core/schemas/messages.py`

Defines structures for inter-service communication.

```python
class MessageSchema(BaseSchema):
    sender: str
    recipient: str
    message_type: MessageType
    content: Dict[str, Any]
    priority: MessagePriority = MessagePriority.NORMAL
    status: MessageStatus = MessageStatus.PENDING
    correlation_id: Optional[str] = None
```

### 3. Task Schemas
**Location**: `core/schemas/tasks.py`

Defines task-related data structures.

```python
class TaskSchema(BaseSchema):
    name: str
    description: str
    status: TaskStatus
    priority: TaskPriority
    assigned_to: Optional[str]
    deadline: Optional[datetime]
    dependencies: List[str] = Field(default_factory=list)
    progress: float = Field(ge=0, le=100, default=0)
```

## Common Enums

### 1. Status Enums
```python
class Status(str, Enum):
    PENDING = "pending"
    ACTIVE = "active"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class Priority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"
```

### 2. Type Enums
TODO: Fill in
```

## Validation Rules

### 1. Common Validators
```python
class Validators:
    @classmethod
    def validate_version(cls, v: str) -> str:
        if not re.match(r"^\d+\.\d+\.\d+$", v):
            raise ValueError("Invalid version format")
        return v

    @classmethod
    def validate_identifier(cls, v: str) -> str:
        if not re.match(r"^[a-zA-Z0-9_-]+$", v):
            raise ValueError("Invalid identifier format")
        return v
```

### 2. Custom Field Types
```python
class CustomFields:
    VersionField = Field(validator=Validators.validate_version)
    IdentifierField = Field(validator=Validators.validate_identifier)
    PositiveFloat = Field(ge=0.0)
    Percentage = Field(ge=0, le=100)
```

## Best Practices

### 1. Schema Definition
```python
class UserSchema(BaseSchema):
    username: str = Field(min_length=3, max_length=50)
    email: EmailStr
    role: UserRole
    active: bool = True
    last_login: Optional[datetime] = None

    class Config:
        schema_extra = {
            "example": {
                "username": "john_doe",
                "email": "john@example.com",
                "role": "user"
            }
        }
```

### 2. Schema Validation
```python
async def validate_data(data: Dict[str, Any], schema_class: Type[BaseSchema]):
    try:
        validated = schema_class(**data)
        return validated
    except ValidationError as e:
        logger.error(f"Validation error: {e.json()}")
        raise SchemaValidationError(e.errors())
```

## Error Handling

```python
class SchemaError(Exception):
    """Base schema error"""
    pass

class ValidationError(SchemaError):
    """Validation error with details"""
    def __init__(self, errors: List[Dict[str, Any]]):
        self.errors = errors
        super().__init__(f"Validation failed: {errors}")
```

## Schema Versioning

```python
class VersionedSchema(BaseSchema):
    schema_version: str = "1.0.0"

    @classmethod
    def upgrade_schema(cls, data: Dict[str, Any], from_version: str) -> Dict[str, Any]:
        """Upgrade data from older schema version"""
        if from_version == "0.9.0":
            # Apply migration rules
            data = cls._migrate_0_9_to_1_0(data)
        return data
```

## Common Usage Patterns

### 1. Data Validation
```python
async def process_message(data: Dict[str, Any]):
    try:
        message = MessageSchema(**data)
        await handle_validated_message(message)
    except ValidationError as e:
        await handle_validation_error(e)
```

### 2. Schema Evolution
```python
async def handle_data(data: Dict[str, Any]):
    version = data.get("schema_version", "1.0.0")
    if version != CURRENT_SCHEMA_VERSION:
        data = await migrate_schema(data, version)
    return await validate_schema(data)
```

### 3. Response Formatting
```python
async def format_response(data: Any) -> ResponseSchema:
    return ResponseSchema(
        status="success",
        data=data,
        metadata={
            "timestamp": datetime.utcnow(),
            "version": CURRENT_VERSION
        }
    )
```

## Integration Examples

### 1. API Integration
```python
@router.post("/tasks")
async def create_task(task: TaskSchema):
    validated_task = await validate_task_schema(task)
    return await task_service.create(validated_task)
```

### 2. Database Integration
```python
async def save_to_db(data: BaseSchema):
    return await db.insert(
        data.dict(exclude_unset=True)
    )
```

## Testing

Example test cases:
```python
def test_schema_validation():
    # Valid data
    data = {
        "name": "Test Task",
        "priority": "high",
        "status": "pending"
    }
    task = TaskSchema(**data)
    assert task.name == "Test Task"

    # Invalid data
    with pytest.raises(ValidationError):
        TaskSchema(name="", priority="invalid")
```

## Development Guidelines

1. Always define clear schema structures
2. Include field validation rules
3. Provide schema documentation
4. Handle version migrations
5. Include example data
6. Test edge cases
7. Monitor validation performance

## Performance Considerations

1. Cache validated schemas when possible
2. Use appropriate field types
3. Optimize validation rules
4. Monitor validation times
5. Batch validate when possible

For more detailed examples and advanced usage patterns, refer to the tests in `tests/core/schemas/`.

Remember to keep schemas:
- Well-documented
- Properly validated
- Version controlled
- Performance optimized
- Consistently structured
