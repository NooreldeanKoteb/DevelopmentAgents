from typing import Type, Dict, Any, Optional
import json
from pydantic import ValidationError
from .base import BaseSchema, SchemaVersion, ValidationResult
from .transformers import SchemaTransformer
from core.config import monitor_operation
from .errors import SchemaValidationError
from .reporting import SchemaViolationReporter
from .registry import SchemaRegistry
from uuid import uuid4

class SchemaValidator:
    """Handles schema validation and transformation."""
    
    def __init__(self):
        self.transformer = SchemaTransformer()
        self.reporter = SchemaViolationReporter()
        self.registry = SchemaRegistry()
        self._validation_errors: Dict[str, list] = {}
    
    @monitor_operation(agent_type="schema_validator", operation="validate")
    async def validate(
        self,
        data: Dict[str, Any],
        schema_class: Type[BaseSchema],
        transform: bool = True
    ) -> ValidationResult:
        """Validate data against a schema."""
        try:
            # Determine schema version
            target_version = schema_class.model_fields["schema_version"].default
            current_version = data.get("schema_version", SchemaVersion.V1)
            
            # Transform if needed
            transformed_data = data
            if transform and current_version != target_version:
                transformed_data = await self.transformer.transform(
                    data,
                    from_version=current_version,
                    to_version=target_version
                )
            
            # Validate against schema
            validated_data = schema_class.model_validate(transformed_data)
            
            return ValidationResult(
                is_valid=True,
                transformed_data=transformed_data if transform else None,
                original_data=data,
                schema_version=target_version
            )
            
        except ValidationError as e:
            # Record validation error
            error_id = str(uuid4())
            self._validation_errors[error_id] = e.errors()
            
            # Report violation
            await self.reporter.report_violation(
                error_id=str(uuid4()),
                schema_class=schema_class.__name__,
                errors=e.errors(),
                data=data
            )
            
            raise SchemaValidationError(
                message="Schema validation failed",
                code="validation_error",
                details={
                    "error_id": error_id,
                    "errors": e.errors(),
                    "schema": schema_class.__name__
                }
            )
    
    async def get_validation_errors(self, error_id: str) -> Optional[list]:
        """Retrieve validation errors by ID."""
        return self._validation_errors.get(error_id) 