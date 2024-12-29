from typing import Dict, Any, List, Optional
from datetime import datetime
from agents.director.persistence import PersistenceManager
from .schemas import TaskSchema
from .errors import TaskManagementError
from .enums import BusinessImpact
from core.schemas.enums import Status, Priority

class TaskManager:
    def __init__(self, persistence: PersistenceManager):
        self.persistence = persistence
        self.tasks: Dict[str, TaskSchema] = {}

    async def get_tasks(self) -> List[Dict[str, Any]]:
        """Retrieve all current tasks."""
        return await self.persistence.get_all_tasks()

    async def add_task(self, task_data: Dict[str, Any]) -> TaskSchema:
        """Add a new task to the system."""
        task = TaskSchema(
            **task_data,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        await self.persistence.save_task(task.id, task.model_dump())
        return task

    async def update_task(self, task_id: str, updates: Dict[str, Any]) -> TaskSchema:
        """Update an existing task."""
        existing_task = await self.persistence.get_task(task_id)
        if not existing_task:
            raise ValueError(f"Task {task_id} not found")
        
        # Update task data
        updated_data = existing_task.model_dump()
        updated_data.update(updates)
        updated_data["updated_at"] = datetime.utcnow()
        
        updated_task = TaskSchema(**updated_data)
        await self.persistence.save_task(task_id, updated_task.model_dump())
        return updated_task

    async def delete_task(self, task_id: str) -> None:
        """Remove a task from the system."""
        if task_id not in self.tasks:
            raise ValueError(f"Task {task_id} not found")
        await self.persistence.delete_task(task_id)

    async def get_task_by_id(self, task_id: str) -> TaskSchema:
        """Retrieve a specific task by ID."""
        if task_id not in self.tasks:
            raise ValueError(f"Task {task_id} not found")
        return self.tasks[task_id]

    async def get_tasks_by_status(self, status: str) -> List[TaskSchema]:
        """Retrieve all tasks with a specific status."""
        return [task for task in self.tasks.values() if task.status == status]

    async def get_tasks_by_agent(self, agent_id: str) -> List[TaskSchema]:
        """Retrieve all tasks assigned to a specific agent."""
        return [task for task in self.tasks.values() if task.assigned_to == agent_id]

    async def create_task(self, task_data: Dict[str, Any]) -> TaskSchema:
        """Create a new task."""
        task = TaskSchema(**task_data)
        self.tasks[task.id] = task
        return task

    async def get_tasks_by_priority(self, priority: Priority) -> List[TaskSchema]:
        """Get all tasks with specified priority."""
        return [
            task for task in self.tasks.values() 
            if task.priority == priority
        ]

    async def update_task_status(
        self,
        tasks: List[TaskSchema],
        task_id: str,
        new_status: Status
    ) -> List[TaskSchema]:
        """Update task status and manage dependencies."""
        try:
            task_map = {task.id: task for task in tasks}
            
            if task_id not in task_map:
                # Return original tasks instead of raising error
                return tasks
                
            task = task_map[task_id]
            task.status = new_status
            
            if new_status == Status.COMPLETED:
                # Update dependent tasks
                for dependent_task in tasks:
                    if task_id in dependent_task.dependencies:
                        if all(
                            task_map[dep].status == Status.COMPLETED
                            for dep in dependent_task.dependencies
                        ):
                            dependent_task.status = Status.PENDING
                            
            return list(task_map.values())
            
        except Exception as e:
            raise TaskManagementError(
                f"Failed to update task status: {str(e)}"
            )
            
    async def create_tasks(
        self,
        plan: Dict[str, Any]
    ) -> List[TaskSchema]:
        """Create tasks from project plan."""
        try:
            tasks = []
            
            for phase in plan["phases"]:
                for task_spec in phase["tasks"]:
                    # Convert business_impact string to enum if needed
                    business_impact = task_spec["business_impact"]
                    if isinstance(business_impact, str):
                        business_impact = BusinessImpact[business_impact]
                    
                    task = TaskSchema(
                        id=f"task-{len(tasks)+1}",
                        name=task_spec["name"],
                        description=task_spec["description"],
                        status=Status.PENDING,
                        priority=self._determine_priority(task_spec),
                        phase=phase["name"]
                    )
                    tasks.append(task)
                    
            return tasks
            
        except Exception as e:
            raise TaskManagementError(f"Failed to create tasks: {str(e)}")
            
    async def update_tasks(
        self,
        current_tasks: List[TaskSchema],
        updated_plan: Dict[str, Any]
    ) -> List[TaskSchema]:
        """Update tasks based on plan changes."""
        try:
            task_map = {task.id: task for task in current_tasks}
            updated_tasks = []
            
            for phase in updated_plan["phases"]:
                for task_spec in phase["tasks"]:
                    task_id = task_spec.get("id")
                    
                    if task_id and task_id in task_map:
                        # Update existing task
                        task = task_map[task_id]
                        task.name = task_spec["name"]
                        task.description = task_spec["description"]
                        task.dependencies = task_spec.get("dependencies", [])
                        task.estimated_duration = task_spec["estimated_duration"]
                        task.phase = phase["name"]
                    else:
                        # Create new task
                        task = TaskSchema(
                            id=f"task-{len(updated_tasks)+1}",
                            name=task_spec["name"],
                            description=task_spec["description"],
                            status=Status.PENDING,
                            priority=self._determine_priority(task_spec),
                            phase=phase["name"]
                        )
                        
                    updated_tasks.append(task)
                    
            return updated_tasks
            
        except Exception as e:
            raise TaskManagementError(f"Failed to update tasks: {str(e)}")
            
    def _determine_priority(self, task_spec: Dict[str, Any]) -> Priority:
        """Determine task priority based on specifications."""
        if task_spec.get("critical", False):
            return Priority.CRITICAL
        elif task_spec.get("high_priority", False):
            return Priority.HIGH
        elif task_spec.get("low_priority", False):
            return Priority.LOW
        return Priority.MEDIUM