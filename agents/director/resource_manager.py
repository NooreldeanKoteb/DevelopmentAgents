from typing import Dict, List, Any, Optional
from datetime import datetime
from core.schemas import ResourceSchema
from .schemas import TaskSchema
from .errors import ResourceError

class ResourceManager:
    """Manages project resources and their allocation."""
    
    def __init__(self):
        """Initialize the resource manager."""
        # Initialize with default resources
        self.resources = {
            "developers": {
                "backend": {"available": 2, "total": 2},
                "frontend": {"available": 2, "total": 2},
                "devops": {"available": 1, "total": 1}
            },
            "compute": {
                "cpu": {"available": 16, "total": 16},
                "memory": {"available": 32, "total": 32},
                "storage": {"available": 1000, "total": 1000}
            },
            "services": {
                "database": {"available": 1, "total": 1},
                "cache": {"available": 1, "total": 1},
                "queue": {"available": 1, "total": 1}
            }
        }
        self.allocations = {}  # Track resource allocations by task
        
    async def allocate_resources(self, tasks: List[TaskSchema]) -> Dict[str, Any]:
        """Allocate resources for a list of tasks.
        
        Args:
            tasks: List of tasks requiring resources
            
        Returns:
            Dict containing resource allocations
        """
        try:
            allocations = {}
            for task in tasks:
                # Get resource requirements, default to empty dict if not specified
                required_resources = getattr(task, 'resources', {})
                
                # Skip resource allocation if no resources required
                if not required_resources:
                    continue
                    
                # Verify resources are available
                if not self._check_resource_availability(required_resources):
                    raise ResourceError(f"Insufficient resources for task: {task.id}")
                    
                # Allocate resources
                allocation = self._allocate_task_resources(task.id, required_resources)
                allocations[task.id] = allocation
                
            return allocations
            
        except Exception as e:
            raise ResourceError(f"Failed to allocate resources: {str(e)}")
            
    def _check_resource_availability(self, required_resources: Dict[str, Any]) -> bool:
        """Check if required resources are available."""
        for resource_type, requirements in required_resources.items():
            if resource_type not in self.resources:
                return False
                
            for resource, amount in requirements.items():
                if resource not in self.resources[resource_type]:
                    return False
                if self.resources[resource_type][resource]["available"] < amount:
                    return False
                    
        return True
        
    def _allocate_task_resources(
        self,
        task_id: str,
        required_resources: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Allocate resources for a specific task."""
        allocation = {}
        
        for resource_type, requirements in required_resources.items():
            allocation[resource_type] = {}
            for resource, amount in requirements.items():
                self.resources[resource_type][resource]["available"] -= amount
                allocation[resource_type][resource] = amount
                
        self.allocations[task_id] = allocation
        return allocation
        
    async def release_resources(self, task_id: str) -> None:
        """Release resources allocated to a task."""
        if task_id not in self.allocations:
            return
            
        allocation = self.allocations[task_id]
        for resource_type, resources in allocation.items():
            for resource, amount in resources.items():
                self.resources[resource_type][resource]["available"] += amount
                
        del self.allocations[task_id]
        
    async def get_resources(self) -> Dict[str, Any]:
        """Get current resource availability."""
        return self.resources
        
    async def update_resource_status(
        self,
        resource_id: str,
        status: str
    ) -> None:
        """Update status of a specific resource."""
        resource_type, resource = resource_id.split(":")
        if resource_type in self.resources and resource in self.resources[resource_type]:
            self.resources[resource_type][resource]["status"] = status