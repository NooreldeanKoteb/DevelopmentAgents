from typing import Dict, Any, Optional, List
import json
from datetime import datetime
from contextlib import asynccontextmanager

import redis.asyncio as redis
from redis.exceptions import RedisError

from agents.project_manager.enums import Priority
from agents.project_manager.models import TaskData, ResourceData

class PersistenceManager:
    def __init__(self, redis_url: str = "redis://localhost:6379") -> None:
        self.redis = redis.from_url(redis_url, decode_responses=True)
        self.task_prefix = "task:"
        self.resource_prefix = "resource:"
        
        # TTL configurations in seconds
        self.ttls = {
            "task": 60 * 60 * 2,     # 2 hours
            "resource": 60 * 60,      # 1 hour
            "active": 60 * 30,        # 30 minutes
            "completed": 60 * 60      # 1 hour
        }

    async def save_task(self, task_id: str, task_data: Dict[str, Any]) -> None:
        """Save task data with proper serialization and TTL."""
        key = f"{self.task_prefix}{task_id}"
        
        # Ensure proper datetime serialization
        task_model = TaskData(**task_data)
        serialized_data = task_model.model_dump_json()
        
        # Set appropriate TTL based on task status
        ttl = self.ttls["completed"] if task_data.get("status") == "completed" else self.ttls["task"]
        
        await self.redis.set(key, serialized_data, ex=ttl)
        
        # Update task index
        await self._update_task_index(task_id, task_data.get("status"))

    async def save_resource(self, resource_id: str, resource_data: Dict[str, Any]) -> None:
        """Save resource data with proper serialization and TTL."""
        key = f"{self.resource_prefix}{resource_id}"
        
        # Ensure proper data serialization
        resource_model = ResourceData(**resource_data)
        serialized_data = resource_model.model_dump_json()
        
        # Set TTL based on resource status
        ttl = self.ttls["active"] if resource_data.get("status") == "active" else self.ttls["resource"]
        
        await self.redis.set(key, serialized_data, ex=ttl)
        
        # Update resource index
        await self._update_resource_index(resource_id, resource_data.get("type"))

    async def get_task(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve and deserialize task data."""
        key = f"{self.task_prefix}{task_id}"
        data = await self.redis.get(key)
        
        if data:
            return TaskData.model_validate_json(data).model_dump()
        return None

    async def get_resource(self, resource_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve and deserialize resource data."""
        key = f"{self.resource_prefix}{resource_id}"
        data = await self.redis.get(key)
        
        if data:
            return ResourceData.model_validate_json(data).model_dump()
        return None

    async def _update_task_index(self, task_id: str, status: str) -> None:
        """Maintain task indices for efficient querying."""
        status_key = f"index:tasks:{status}"
        await self.redis.sadd(status_key, task_id)
        await self.redis.expire(status_key, self.ttls["task"])

    async def _update_resource_index(self, resource_id: str, resource_type: str) -> None:
        """Maintain resource indices for efficient querying."""
        type_key = f"index:resources:{resource_type}"
        await self.redis.sadd(type_key, resource_id)
        await self.redis.expire(type_key, self.ttls["resource"])

    async def get_tasks_by_status(self, status: str) -> List[Dict[str, Any]]:
        """Retrieve all tasks with a specific status."""
        status_key = f"index:tasks:{status}"
        task_ids = await self.redis.smembers(status_key)
        
        tasks = []
        for task_id in task_ids:
            task_data = await self.get_task(task_id)
            if task_data:
                tasks.append(task_data)
                
        return tasks

    async def get_resources_by_type(self, resource_type: str) -> List[Dict[str, Any]]:
        """Retrieve all resources of a specific type."""
        type_key = f"index:resources:{resource_type}"
        resource_ids = await self.redis.smembers(type_key)
        
        resources = []
        for resource_id in resource_ids:
            resource_data = await self.get_resource(resource_id)
            if resource_data:
                resources.append(resource_data)
                
        return resources