from typing import Dict, Any
from .base import SchemaVersion
from .errors import SchemaTransformError

class SchemaTransformer:
    """Handles schema version transformations."""
    
    async def transform(
        self,
        data: Dict[str, Any],
        from_version: SchemaVersion,
        to_version: SchemaVersion
    ) -> Dict[str, Any]:
        """Transform data between schema versions."""
        try:
            if from_version == to_version:
                return data
                
            # Get transformation path
            path = self._get_transformation_path(from_version, to_version)
            
            # Apply transformations sequentially
            transformed_data = data.copy()
            for start, end in zip(path[:-1], path[1:]):
                transform_method = self._get_transform_method(start, end)
                transformed_data = await transform_method(transformed_data)
            
            return transformed_data
            
        except Exception as e:
            raise SchemaTransformError(
                message="Schema transformation failed",
                code="transform_error",
                details={
                    "from_version": from_version,
                    "to_version": to_version,
                    "error": str(e)
                }
            )
    
    def _get_transformation_path(
        self,
        from_version: SchemaVersion,
        to_version: SchemaVersion
    ) -> list:
        """Get the path of transformations needed."""
        versions = list(SchemaVersion)
        start_idx = versions.index(from_version)
        end_idx = versions.index(to_version)
        
        if start_idx < end_idx:
            return versions[start_idx:end_idx + 1]
        return list(reversed(versions[end_idx:start_idx + 1]))
    
    def _get_transform_method(
        self,
        from_version: SchemaVersion,
        to_version: SchemaVersion
    ):
        """Get the appropriate transformation method."""
        method_name = f"_transform_{from_version}_to_{to_version}"
        return getattr(self, method_name, self._transform_default)
    
    async def _transform_v1_to_v1_1(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Transform from V1 to V1.1 schema."""
        transformed = data.copy()
        
        # Example transformation logic
        if "metadata" in transformed:
            transformed["meta"] = transformed.pop("metadata")
        
        return transformed
    
    async def _transform_v1_1_to_v2(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Transform from V1.1 to V2 schema."""
        transformed = data.copy()
        
        # Example transformation logic
        if "metadata" in transformed:
            transformed["meta"] = transformed.pop("metadata")
        
        return transformed 