from typing import Dict, Type, Optional
from .base import BaseSchema
from .version import SchemaVersion

class SchemaRegistry:
    """Central registry for schema management."""
    
    _instance = None
    _schemas: Dict[str, Type[BaseSchema]] = {}
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def register(self, schema: Type[BaseSchema]) -> None:
        """Register a schema."""
        schema_name = schema.__name__
        self._schemas[schema_name] = schema
    
    def get_schema(self, name: str) -> Optional[Type[BaseSchema]]:
        """Get a registered schema by name."""
        return self._schemas.get(name)
    
    def list_schemas(self) -> Dict[str, Type[BaseSchema]]:
        """List all registered schemas."""
        return self._schemas.copy()
    
    def validate_schema_compatibility(
        self,
        schema: Type[BaseSchema],
        version: SchemaVersion
    ) -> bool:
        """Validate schema compatibility with a specific version."""
        current_version = getattr(schema, 'version', None)
        if not current_version:
            return False
            
        # Only allow backward compatibility within same major version
        return (current_version.major == version.major and 
                current_version.minor >= version.minor)
    