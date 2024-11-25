from typing import Dict, Any, Optional, List, Union
import redis.asyncio as aioredis
from redis.asyncio import Redis
from datetime import datetime
import json
from enum import Enum

from core.schemas.enums import (
    ResourceType,
    ResourceStatus,
    TaskStatus,
    TaskPriority,
    BusinessImpact
)
from core.schemas.resource import ResourceSchema
from core.schemas.task import TaskSchema

class PersistenceManager:
    def __init__(self, redis_url: Optional[str] = None, redis_client: Optional[Redis] = None):
        if redis_client:
            self.redis = redis_client
        elif redis_url:
            self.redis = aioredis.from_url(redis_url)
        else:
            self.redis = aioredis.from_url("redis://localhost:6379/0")

    def _serialize_value(self, value: Any) -> str:
        """Serialize a single value for Redis storage."""
        if isinstance(value, datetime):
            return value.isoformat()
        elif isinstance(value, (list, dict)):
            return json.dumps(value)
        elif isinstance(value, Enum):
            return value.value
        return str(value)

    def _deserialize_value(self, prefix: str, key: str, value: str) -> Any:
        """Deserialize a value based on key name and prefix."""
        try:
            if key == 'status':
                if prefix.startswith("task:"):
                    return TaskStatus(value)
                else:
                    return ResourceStatus(value)
            elif key == 'type':
                return ResourceType(value.lower())
            elif key == 'priority':
                return TaskPriority(value)
            elif key == 'business_impact':
                return BusinessImpact(value)
            elif key in ('dependencies', 'tags', 'subtasks', 'completion_criteria', 'capabilities'):
                # Handle list fields
                return json.loads(value) if value and value != '[]' else []
            elif key in ('metadata', 'requirements', 'limits'):
                # Handle dict fields - added 'limits' here
                if not value or value == '{}' or value.lower() == 'none':
                    return {}
                return json.loads(value)
            elif key in ('capacity', 'current_load', 'current_usage', 'performance_score', 'estimated_duration', 'progress'):
                return float(value)
            elif key in ('created_at', 'updated_at', 'due_date') and value and value.lower() != 'none':
                return datetime.fromisoformat(value)
            elif key == 'due_date' and (not value or value.lower() == 'none'):
                return None
            elif value == 'None':
                return None
            return value
        except (ValueError, json.JSONDecodeError) as e:
            print(f"Error deserializing {key}: {value} - {str(e)}")
            if key in ('metadata', 'requirements', 'limits'):
                return {}
            elif key in ('dependencies', 'tags', 'subtasks', 'completion_criteria', 'capabilities'):
                return []
            return value

    def _serialize_data(self, data: Dict[str, Any]) -> Dict[str, str]:
        """Serialize data for Redis storage."""
        return {str(k): self._serialize_value(v) for k, v in data.items()}

    def _deserialize_data(self, prefix: str, data: Dict[bytes, bytes]) -> Dict[str, Any]:
        """Deserialize data from Redis storage."""
        deserialized = {}
        for key, value in data.items():
            key_str = key.decode('utf-8')
            value_str = value.decode('utf-8')
            deserialized[key_str] = self._deserialize_value(prefix, key_str, value_str)
        return deserialized

    async def get_task(self, task_id: str) -> Optional[TaskSchema]:
        """Get task by ID."""
        data = await self.redis.hgetall(f"task:{task_id}")
        if not data:
            return None
        deserialized = self._deserialize_data("task:", data)
        return TaskSchema.model_validate(deserialized)

    async def save_task(self, task_id: Union[str, TaskSchema, Dict], task_data: Optional[Union[TaskSchema, Dict]] = None) -> None:
        """Save task data to Redis.
        Can be called as either:
        - save_task(task_schema)  # Single argument form
        - save_task(task_id, task_data)  # Two argument form
        """
        # Handle single argument form
        if isinstance(task_id, (TaskSchema, dict)) and task_data is None:
            task_data = task_id
            task_id = task_data.id if isinstance(task_data, TaskSchema) else task_data.get('id')
            if not task_id:
                raise ValueError("Task ID is required")
        
        # Handle two argument form
        elif isinstance(task_id, str):
            if task_data is None:
                raise ValueError("Task data is required when providing task_id as string")
        else:
            raise ValueError("Invalid arguments provided to save_task")

        # Convert dict to TaskSchema if needed
        if isinstance(task_data, dict):
            task_data = TaskSchema.model_validate(task_data)
        elif not isinstance(task_data, TaskSchema):
            raise ValueError("Task data must be TaskSchema or dict")

        task_dict = task_data.model_dump()
        serialized = self._serialize_data(task_dict)
        await self.redis.hset(f"task:{task_id}", mapping=serialized)
        await self.redis.sadd("tasks", task_id)

    async def delete_task(self, task_id: str) -> None:
        """Delete a task."""
        await self.redis.delete(f"task:{task_id}")

    async def list_tasks(self, status: Optional[TaskStatus] = None) -> List[TaskSchema]:
        """List tasks with optional status filter."""
        task_ids = await self.redis.smembers("tasks")
        tasks = []
        
        for task_id in task_ids:
            task_id = task_id.decode('utf-8')
            task = await self.get_task(task_id)
            if task and (status is None or task.status == status):
                tasks.append(task)
        return tasks

    async def save_resource(self, resource_id: Union[str, ResourceSchema, Dict], resource_data: Optional[Union[ResourceSchema, Dict]] = None) -> None:
        """Save resource data to Redis.
        Can be called as either:
        - save_resource(resource_schema)  # Single argument form
        - save_resource(resource_id, resource_data)  # Two argument form
        """
        # Handle single argument form
        if isinstance(resource_id, (ResourceSchema, dict)) and resource_data is None:
            resource_data = resource_id
            resource_id = resource_data.id if isinstance(resource_data, ResourceSchema) else resource_data.get('id')
            if not resource_id:
                raise ValueError("Resource ID is required")
        
        # Handle two argument form
        elif isinstance(resource_id, str):
            if resource_data is None:
                raise ValueError("Resource data is required when providing resource_id as string")
        else:
            raise ValueError("Invalid arguments provided to save_resource")

        # Convert dict to ResourceSchema if needed
        if isinstance(resource_data, dict):
            resource_data = ResourceSchema.model_validate(resource_data)
        elif not isinstance(resource_data, ResourceSchema):
            raise ValueError("Resource data must be ResourceSchema or dict")

        resource_dict = resource_data.model_dump()
        serialized = self._serialize_data(resource_dict)
        await self.redis.hset(f"resource:{resource_id}", mapping=serialized)
        await self.redis.sadd("resources", resource_id)

    async def get_resource(self, resource_id: str) -> Optional[ResourceSchema]:
        """Get resource by ID."""
        data = await self.redis.hgetall(f"resource:{resource_id}")
        if not data:
            return None
        deserialized = self._deserialize_data("resource:", data)
        return ResourceSchema.model_validate(deserialized)

    async def delete_resource(self, resource_id: str) -> None:
        """Delete a resource."""
        await self.redis.delete(f"resource:{resource_id}")

    async def assign_resource_to_task(self, task_id: str, resource_id: str) -> None:
        """Assign a resource to a task."""
        task = await self.get_task(task_id)
        resource = await self.get_resource(resource_id)
        
        if not task or not resource:
            raise ValueError("Task or resource does not exist")
        
        await self.redis.sadd(f"task:{task_id}:resources", resource_id)
        await self.redis.sadd(f"resource:{resource_id}:tasks", task_id)

    async def unassign_resource_from_task(self, task_id: str, resource_id: str) -> None:
        """Unassign a resource from a task."""
        await self.redis.srem(f"task:{task_id}:resources", resource_id)
        await self.redis.srem(f"resource:{resource_id}:tasks", task_id)

    async def get_task_resources(self, task_id: str) -> List[ResourceSchema]:
        """Get resources assigned to a task."""
        resource_ids = await self.redis.smembers(f"task:{task_id}:resources")
        resources = []
        for rid in resource_ids:
            resource = await self.get_resource(rid.decode())
            if resource:
                resources.append(resource)
        return resources

    async def get_resource_tasks(self, resource_id: str) -> List[TaskSchema]:
        """Get tasks assigned to a resource."""
        task_ids = await self.redis.smembers(f"resource:{resource_id}:tasks")
        tasks = []
        for tid in task_ids:
            task = await self.get_task(tid.decode())
            if task:
                tasks.append(task)
        return tasks