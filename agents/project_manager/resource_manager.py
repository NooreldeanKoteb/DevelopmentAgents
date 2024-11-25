from typing import Dict, Any, List, Optional, Union
from datetime import datetime
import asyncio
from enum import Enum
from pydantic import BaseModel
from agents.project_manager.persistence import PersistenceManager

from core.schemas.agent import AgentStatus
from core.schemas.enums import (
    TaskStatus,
    ResourceStatus,
    ResourceType
)
from core.schemas import (
    TaskSchema,
    ResourceSchema
)
from .errors import ResourceManagementError

class ResourceManager:
    """Manages resource allocation and optimization."""
    
    def __init__(self, persistence_manager: Optional[PersistenceManager] = None):
        """Initialize resource manager."""
        self.persistence = persistence_manager or PersistenceManager()
        
    async def allocate_resources(
        self,
        tasks: List[TaskSchema]
    ) -> Dict[str, ResourceSchema]:
        """Allocate resources to tasks."""
        try:
            allocations = {}
            
            for task in tasks:
                # Determine required resources
                required_resources = self._determine_requirements(task)
                
                # Find available resources
                available_resources = self._find_available_resources(
                    required_resources
                )
                
                if not available_resources:
                    raise ResourceManagementError(
                        f"Insufficient resources for task {task.id}"
                    )
                    
                # Allocate resources
                allocations[task.id] = {
                    "resources": available_resources,
                    "allocated_at": datetime.now().isoformat()
                }
                
                # Update resource status
                for resource in available_resources:
                    resource.status = ResourceStatus.IN_USE
                    resource.allocated_to = task.id
                    
            return allocations
            
        except Exception as e:
            raise ResourceManagementError(
                f"Failed to allocate resources: {str(e)}"
            )
            
    async def reallocate_resources(
        self,
        tasks: List[TaskSchema],
        current_allocations: Dict[str, ResourceSchema]
    ) -> Dict[str, ResourceSchema]:
        """Reallocate resources based on changes."""
        try:
            # Release completed task resources
            self._release_completed_resources(tasks, current_allocations)
            
            # Allocate resources for pending tasks
            pending_tasks = [
                task for task in tasks
                if not task.id in current_allocations
            ]
            
            new_allocations = await self.allocate_resources(pending_tasks)
            
            return {**current_allocations, **new_allocations}
            
        except Exception as e:
            raise ResourceManagementError(
                f"Failed to reallocate resources: {str(e)}"
            )
            
    async def update_agent_status(
        self,
        agent_id: str,
        status: AgentStatus
    ) -> None:
        """Update agent status and availability."""
        if agent_id in self.agents:
            self.agents[agent_id].status = status
            
            # Update associated resources
            for resource in self.resources.values():
                if resource.allocated_to == agent_id:
                    if status == AgentStatus.OFFLINE:
                        resource.status = ResourceStatus.UNAVAILABLE
                    elif status == AgentStatus.IDLE:
                        resource.status = ResourceStatus.AVAILABLE
                        
    async def update_resource_status(
        self,
        resource_id: str,
        status: ResourceStatus
    ) -> None:
        """Update resource status."""
        if resource_id in self.resources:
            self.resources[resource_id].status = status
            
    def _determine_requirements(
        self,
        task: TaskSchema
    ) -> Dict[str, Any]:
        """Determine resource requirements for a task."""
        # Implementation would analyze task requirements
        # For now, return placeholder requirements
        return {
            "cpu": 1,
            "memory": 1024,
            "agents": ["python", "testing"]
        }
        
    def _find_available_resources(
        self,
        requirements: Dict[str, Any]
    ) -> List[ResourceSchema]:
        """Find available resources matching requirements."""
        available = []
        
        for resource in self.resources.values():
            if (resource.status == ResourceStatus.AVAILABLE and
                self._matches_requirements(resource, requirements)):
                available.append(resource)
                
        return available
        
    def _matches_requirements(
        self,
        resource: ResourceSchema,
        requirements: Dict[str, Any]
    ) -> bool:
        """Check if resource matches requirements."""
        # Implementation would check resource capabilities
        # For now, return simple match
        return True
        
    def _release_completed_resources(
        self,
        tasks: List[TaskSchema],
        allocations: Dict[str, ResourceSchema]
    ) -> None:
        """Release resources from completed tasks."""
        completed_task_ids = {
            task.id for task in tasks
            if task.status == TaskStatus.COMPLETED
        }
        
        for task_id in completed_task_ids:
            if task_id in allocations:
                for resource in allocations[task_id]["resources"]:
                    resource.status = ResourceStatus.AVAILABLE
                    resource.allocated_to = None
                    
    async def create_project_plan(self, project_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a project plan with resource allocation."""
        try:
            tasks = [TaskSchema.model_validate(task) for task in project_data["tasks"]]
            
            # Calculate critical path
            critical_path = self._calculate_critical_path(tasks)
            
            # Create plan
            plan = {
                "name": project_data["name"],
                "tasks": [task.model_dump() for task in tasks],
                "critical_path": critical_path,
                "estimated_duration": sum(task.estimated_duration for task in tasks),
                "created_at": datetime.now().isoformat()
            }
            
            return plan
            
        except Exception as e:
            raise ResourceManagementError(f"Failed to create project plan: {str(e)}")
            
    def _calculate_critical_path(self, tasks: List[TaskSchema]) -> List[str]:
        """Calculate the critical path through tasks."""
        # Simple implementation - just return tasks in dependency order
        ordered_tasks = []
        remaining_tasks = tasks.copy()
        
        while remaining_tasks:
            for task in remaining_tasks[:]:
                if all(dep in [t.id for t in ordered_tasks] for dep in task.dependencies):
                    ordered_tasks.append(task)
                    remaining_tasks.remove(task)
                    
        return [task.id for task in ordered_tasks]
            
    async def allocate_resource(self, resource_id: str, resource_data: Union[ResourceSchema, Dict[str, Any]]) -> Dict[str, Any]:
        """Allocate a new resource."""
        try:
            # Validate and create resource
            if isinstance(resource_data, dict):
                resource = ResourceSchema.model_validate(resource_data)
            else:
                resource = resource_data
            
            # Save to persistence
            await self.persistence.save_resource(resource_id, resource)
            
            return {
                "action_type": "resource_allocation",
                "status": "success",
                "resource_id": resource_id,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            raise ResourceManagementError(f"Failed to allocate resource: {str(e)}")