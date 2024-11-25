from typing import Dict, Any, Optional, List
from datetime import datetime
import asyncio
import uuid

from agents.base import BaseAgent, AgentError
from core.messaging import Message
from core.schemas import (
    AgentType, TaskSchema, TaskStatus, TaskPriority,
    AgentSchema, ResourceSchema
)
from .planner import ProjectPlanner
from .task_manager import TaskManager
from .resource_manager import ResourceManager
from agents.project_manager.persistence import PersistenceManager

class ProjectManagerAgent(BaseAgent):
    """Agent responsible for managing project resources and tasks."""
    
    def __init__(
        self,
        name: str,
        agent_type: str = "project_manager",
        **kwargs
    ):
        super().__init__(
            agent_id=kwargs.get('agent_id', str(uuid.uuid4())),
            name=name,
            agent_type=agent_type
        )
        self.task_service = kwargs.get('task_service')
        self.resource_service = kwargs.get('resource_service')
        self.planner_service = kwargs.get('planner_service')
        
    async def initialize(self) -> None:
        """Initialize project manager components."""
        await super().initialize()
        
        self.planner = ProjectPlanner()
        self.task_manager = TaskManager()
        self.resource_manager = ResourceManager()
        
        # Subscribe to additional topics
        topics = [
            "project.new",
            "project.update",
            "task.status",
            "agent.status",
            "resource.status"
        ]
        
        for topic in topics:
            await self.message_broker.subscribe(topic, self._handle_message)
            
    async def process_message(self, message: Message) -> Optional[Message]:
        """Process incoming messages."""
        try:
            if message.topic == "project.new":
                return await self._handle_new_project(message)
            elif message.topic == "project.update":
                return await self._handle_project_update(message)
            elif message.topic == "task.status":
                return await self._handle_task_status(message)
            elif message.topic == "agent.status":
                return await self._handle_agent_status(message)
            elif message.topic == "resource.status":
                return await self._handle_resource_status(message)
                
        except Exception as e:
            self.logger.logger.error(
                f"Error processing message: {str(e)}",
                extra={"message": message.model_dump()}
            )
            raise AgentError(f"Message processing failed: {str(e)}")
            
    async def _handle_new_project(self, message: Message) -> Message:
        """Handle new project request."""
        project_spec = message.content
        
        # Generate project plan
        plan = await self.planner.create_plan(project_spec)
        
        # Create tasks from plan
        tasks = await self.task_manager.create_tasks(plan)
        
        # Allocate resources
        resources = await self.resource_manager.allocate_resources(tasks)
        
        # Store project context
        await self.save_to_memory(
            f"project:{project_spec['id']}",
            {
                "spec": project_spec,
                "plan": plan,
                "tasks": tasks,
                "resources": resources
            }
        )
        
        return Message(
            topic="project.created",
            content={
                "project_id": project_spec["id"],
                "tasks": tasks,
                "resources": resources
            },
            sender=self.id
        )
        
    async def _handle_project_update(self, message: Message) -> Optional[Message]:
        """Handle project update request."""
        project_id = message.content["project_id"]
        update_type = message.content["type"]
        
        # Retrieve project context
        project_data = await self.recall_from_memory(f"project:{project_id}")
        if not project_data:
            raise AgentError(f"Project {project_id} not found")
            
        if update_type == "modify_plan":
            # Update project plan
            new_plan = await self.planner.update_plan(
                project_data["plan"],
                message.content["changes"]
            )
            project_data["plan"] = new_plan
            
            # Update tasks
            tasks = await self.task_manager.update_tasks(
                project_data["tasks"],
                new_plan
            )
            project_data["tasks"] = tasks
            
        elif update_type == "resource_change":
            # Reallocate resources
            resources = await self.resource_manager.reallocate_resources(
                project_data["tasks"],
                message.content["changes"]
            )
            project_data["resources"] = resources
            
        # Update project context
        await self.save_to_memory(f"project:{project_id}", project_data)
        
        return Message(
            topic="project.updated",
            content={
                "project_id": project_id,
                "update_type": update_type,
                "tasks": project_data["tasks"],
                "resources": project_data["resources"]
            },
            sender=self.id
        )
        
    async def _handle_task_status(self, message: Message) -> Optional[Message]:
        """Handle task status updates."""
        task_id = message.content["task_id"]
        new_status = message.content["status"]
        project_id = message.content["project_id"]
        
        project_data = await self.recall_from_memory(f"project:{project_id}")
        if not project_data:
            raise AgentError(f"Project {project_id} not found")
            
        # Update task status
        updated_tasks = await self.task_manager.update_task_status(
            project_data["tasks"],
            task_id,
            new_status
        )
        project_data["tasks"] = updated_tasks
        
        # Check if project needs reallocation
        if new_status in [TaskStatus.COMPLETED, TaskStatus.FAILED]:
            resources = await self.resource_manager.reallocate_resources(
                updated_tasks,
                project_data["resources"]
            )
            project_data["resources"] = resources
            
        # Update project context
        await self.save_to_memory(f"project:{project_id}", project_data)
        
        return Message(
            topic="project.task.updated",
            content={
                "project_id": project_id,
                "task_id": task_id,
                "status": new_status,
                "tasks": updated_tasks,
                "resources": project_data["resources"]
            },
            sender=self.id
        )
        
    async def _handle_agent_status(self, message: Message) -> Optional[Message]:
        """Handle agent status updates."""
        agent_id = message.content["agent_id"]
        new_status = message.content["status"]
        
        # Update resource manager with agent status
        await self.resource_manager.update_agent_status(agent_id, new_status)
        
        # Check if any projects need resource reallocation
        projects = await self._get_active_projects()
        for project_id in projects:
            project_data = await self.recall_from_memory(f"project:{project_id}")
            if project_data:
                resources = await self.resource_manager.reallocate_resources(
                    project_data["tasks"],
                    project_data["resources"]
                )
                project_data["resources"] = resources
                await self.save_to_memory(f"project:{project_id}", project_data)
                
    async def _handle_resource_status(self, message: Message) -> Optional[Message]:
        """Handle resource status updates."""
        resource_id = message.content["resource_id"]
        new_status = message.content["status"]
        
        # Update resource manager
        await self.resource_manager.update_resource_status(
            resource_id,
            new_status
        )
        
        # Check if any projects need reallocation
        projects = await self._get_active_projects()
        for project_id in projects:
            project_data = await self.recall_from_memory(f"project:{project_id}")
            if project_data:
                resources = await self.resource_manager.reallocate_resources(
                    project_data["tasks"],
                    project_data["resources"]
                )
                project_data["resources"] = resources
                await self.save_to_memory(f"project:{project_id}", project_data)
                
    async def _get_active_projects(self) -> List[str]:
        """Get list of active project IDs."""
        memories = await self.memory.list_memories("project:*")
        return [m["key"].split(":")[-1] for m in memories]
        
    async def execute_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute management task."""
        task_type = task.get("type")
        
        if task_type == "create_project":
            return await self._handle_new_project(Message(
                topic="project.new",
                content=task["project_spec"],
                sender="system"
            ))
        elif task_type == "update_project":
            return await self._handle_project_update(Message(
                topic="project.update",
                content=task["update_spec"],
                sender="system"
            ))
        else:
            raise AgentError(f"Unknown task type: {task_type}")
        
    async def handle_error(self, error: Exception) -> None:
        """Handle agent errors."""
        self.logger.logger.error(f"Error in ProjectManager: {str(error)}")
        self.metrics.error_count.inc()
        # Add any specific error handling logic here