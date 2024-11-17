from core.config.errors import AppError

class SchemaError(AppError):
    """Base schema error."""
    pass

class SchemaValidationError(SchemaError):
    """Schema validation error."""
    pass

class SchemaTransformError(SchemaError):
    """Schema transformation error."""
    pass

class SchemaVersionError(SchemaError):
    """Schema version error."""
    pass 