from typing import Dict, Any, Optional, List, Union, AsyncGenerator
import redis.asyncio as aioredis
import json
from datetime import datetime
from redis.asyncio import Redis, ConnectionPool
from contextlib import asynccontextmanager

from core.schemas import TaskSchema, ResourceSchema, TaskStatus, TaskPriority, BusinessImpact

class PersistenceManager:
    """Manages data persistence using Redis."""
    
    def __init__(self, redis_url: Optional[str] = None, redis_client: Optional[Redis] = None):
        if redis_client:
            self.redis = redis_client
        elif redis_url:
            self.redis = Redis.from_url(redis_url)
        else:
            self.redis = Redis.from_url("redis://localhost:6379/0")
        
    @classmethod
    def from_client(cls, redis_client: Redis) -> 'PersistenceManager':
        """Create instance from existing Redis client."""
        instance = cls.__new__(cls)
        instance.redis = redis_client
        return instance
        
    @asynccontextmanager
    async def get_connection(self) -> AsyncGenerator[Redis, None]:
        """Get Redis connection from pool."""
        conn = Redis(connection_pool=self.pool)
        try:
            yield conn
        finally:
            await conn.close()
            
    async def save_task(self, task_id: str, task_data: Union[Dict, TaskSchema]) -> None:
        """Save task data to Redis."""
        if isinstance(task_data, TaskSchema):
            data = task_data.model_dump()
        else:
            data = task_data.copy()
            
        async with self.get_connection() as redis:
            await redis.hset(
                f"task:{task_id}",
                mapping=data
            )
            
    async def get_task(self, task_id: str) -> Optional[TaskSchema]:
        """Get task data from Redis."""
        async with self.get_connection() as redis:
            data = await redis.hgetall(f"task:{task_id}")
            if not data:
                return None
                
            # Convert string enums back to proper types
            data["status"] = TaskStatus(data["status"])
            data["priority"] = TaskPriority(data["priority"])
            data["business_impact"] = BusinessImpact(data["business_impact"])
            
            return TaskSchema(**data)
            
    async def save_resource(self, resource_id: str, resource_data: Union[Dict, ResourceSchema]) -> None:
        """Save resource data to Redis."""
        if isinstance(resource_data, ResourceSchema):
            data = resource_data.model_dump()
        else:
            data = resource_data.copy()
            
        async with self.get_connection() as redis:
            await redis.hset(
                f"resource:{resource_id}",
                mapping=data
            )
            
    async def get_resource(self, resource_id: str) -> Optional[ResourceSchema]:
        """Get resource data from Redis."""
        async with self.get_connection() as redis:
            data = await redis.hgetall(f"resource:{resource_id}")
            if not data:
                return None
            return ResourceSchema(**data)
            
    async def list_tasks(self, pattern: str = "*") -> List[TaskSchema]:
        """List all tasks matching pattern."""
        async with self.get_connection() as redis:
            keys = await redis.keys(f"task:{pattern}")
            tasks = []
            
            for key in keys:
                data = await redis.hgetall(key)
                if data:
                    # Convert string enums back to proper types
                    data["status"] = TaskStatus(data["status"])
                    data["priority"] = TaskPriority(data["priority"])
                    data["business_impact"] = BusinessImpact(data["business_impact"])
                    tasks.append(TaskSchema(**data))
                    
            return tasks
            
    async def list_resources(self, pattern: str = "*") -> List[ResourceSchema]:
        """List all resources matching pattern."""
        async with self.get_connection() as redis:
            keys = await redis.keys(f"resource:{pattern}")
            resources = []
            
            for key in keys:
                data = await redis.hgetall(key)
                if data:
                    resources.append(ResourceSchema(**data))
                    
            return resources