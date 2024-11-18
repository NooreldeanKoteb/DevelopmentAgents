from typing import List, Dict, Any, Optional
from datetime import datetime
from pydantic import BaseModel
from agents.project_manager.persistence import PersistenceManager

class Task(BaseModel):
    id: str
    name: str
    description: str
    status: str
    assigned_agent: Optional[str]
    dependencies: List[str]
    created_at: datetime
    updated_at: datetime
    estimated_duration: float  # in hours
    priority: str

class TaskManager:
    def __init__(self) -> None:
        self.persistence = PersistenceManager()

    async def get_tasks(self) -> List[Dict[str, Any]]:
        """Retrieve all current tasks."""
        return await self.persistence.get_all_tasks()

    async def add_task(self, task_data: Dict[str, Any]) -> Task:
        """Add a new task to the system."""
        task = Task(
            **task_data,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        await self.persistence.save_task(task.id, task.model_dump())
        return task

    async def update_task(self, task_id: str, updates: Dict[str, Any]) -> Task:
        """Update an existing task."""
        existing_task = await self.persistence.get_task(task_id)
        if not existing_task:
            raise ValueError(f"Task {task_id} not found")
        
        existing_task.update(updates)
        existing_task["updated_at"] = datetime.utcnow().isoformat()
        
        updated_task = Task(**existing_task)
        await self.persistence.save_task(task_id, updated_task.model_dump())
        return updated_task

    async def delete_task(self, task_id: str) -> None:
        """Remove a task from the system."""
        if task_id not in self.tasks:
            raise ValueError(f"Task {task_id} not found")
        del self.tasks[task_id]

    async def get_task_by_id(self, task_id: str) -> Task:
        """Retrieve a specific task by ID."""
        if task_id not in self.tasks:
            raise ValueError(f"Task {task_id} not found")
        return self.tasks[task_id]

    async def get_tasks_by_status(self, status: str) -> List[Task]:
        """Retrieve all tasks with a specific status."""
        return [task for task in self.tasks.values() if task.status == status]

    async def get_tasks_by_agent(self, agent_id: str) -> List[Task]:
        """Retrieve all tasks assigned to a specific agent."""
        return [task for task in self.tasks.values() if task.assigned_agent == agent_id] 