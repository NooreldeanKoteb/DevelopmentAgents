from typing import Dict, Any, Optional, List
from datetime import datetime
import asyncio
import uuid
import json

from agents.base import BaseAgent, AgentError
from agents.base.message import Message as BaseMessage  # Import base Message
from core.messaging.message import Message as CoreMessage  # Import core Message for pub/sub
from core.schemas import (
    AgentType, TaskSchema, TaskStatus, TaskPriority,
    AgentSchema, ResourceSchema
)
from .planner import ProjectPlanner
from .task_manager import TaskManager
from .resource_manager import ResourceManager
from agents.director.persistence import PersistenceManager
from redis import Redis
from core.openai import OpenAIClient, OpenAIError

class DirectorAgent(BaseAgent):
    """Agent responsible for managing project resources and tasks."""
    
    def __init__(
        self,
        name: str,
        agent_type: str,
        task_service: TaskManager,
        resource_service: ResourceManager,
        planner_service: ProjectPlanner,
        redis_client: Optional[Redis] = None,
        redis_url: Optional[str] = None
    ):
        """Initialize the Director agent."""
        self.agent_id = str(uuid.uuid4())  # Set agent_id before super().__init__
        super().__init__(
            agent_id=self.agent_id,
            name=name,
            agent_type=AgentType.DIRECTOR,
            redis_client=redis_client,
            redis_url=redis_url
        )
        
        self.task_service = task_service
        self.resource_service = resource_service
        self.openai = OpenAIClient()  # Initialize OpenAI client here
        
        # Pass self to planner so it can use our OpenAI client
        self.planner_service = planner_service or ProjectPlanner(agent=self)
        
    async def initialize(self) -> None:
        """Initialize Director components."""
        await super().initialize()
        
        # Initialize services if not injected
        if not self.planner_service:
            self.planner_service = ProjectPlanner(agent=self)
        if not self.task_service:
            self.task_service = TaskManager(persistence=PersistenceManager())
        if not self.resource_service:
            self.resource_service = ResourceManager()
        
        # Subscribe to topics using process_message as the callback
        if self.message_broker:
            topics = [
                "project.new",
                "project.update",
                "task.status",
                "agent.status",
                "resource.status"
            ]
            
            for topic in topics:
                await self.message_broker.subscribe(
                    topic=topic,
                    callback=self.process_message  # Use process_message as the callback
                )
        
    async def _handle_message_type(self, message: CoreMessage) -> Any:
        """Handle different types of project management messages."""
        # Handle messages based on topic if present
        if hasattr(message, 'topic') and message.topic:
            topic_handlers = {
                "project.new": self._handle_new_project,
                "project.update": self._handle_project_update,
                "task.status": self._handle_task_status,
                "agent.status": self._handle_agent_status,
                "resource.status": self._handle_resource_status
            }
            if message.topic in topic_handlers:
                return await topic_handlers[message.topic](message)
        
        # Fall back to type-based handling
        type_handlers = {
            "task.create": self._handle_task_creation,
            "task.update": self._handle_task_status,
            "project.create": self._handle_new_project,
            "project.update": self._handle_project_update
        }
        
        if message.type not in type_handlers:
            raise AgentError(f"Unsupported message type: {message.type}")
            
        return await type_handlers[message.type](message)
        
    async def _handle_new_project(self, message: CoreMessage) -> CoreMessage:
        """Handle new project request."""
        project_spec = message.content
        
        # Generate project plan using planner_service instead of planner
        plan = await self.planner_service.create_plan(project_spec)
        
        # Create tasks from plan using task_service
        tasks = await self.task_service.create_tasks(plan)
        
        # Allocate resources
        resources = await self.resource_service.allocate_resources(tasks)
        
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
        
        return CoreMessage(
            topic="project.created",
            content={
                "project_id": project_spec['id'],
                "plan": plan,
                "tasks": tasks,
                "resources": resources
            },
            sender=self.agent_id
        )
        
    async def _handle_project_update(self, message: CoreMessage) -> Optional[CoreMessage]:
        """Handle project update request."""
        project_id = message.content["project_id"]
        update_type = message.content["type"]
        
        # Retrieve project context and parse JSON
        project_data_str = await self.recall_from_memory(f"project:{project_id}")
        if not project_data_str:
            raise AgentError(f"Project {project_id} not found")
        
        project_data = json.loads(project_data_str)  # Parse the JSON string into a dict
        
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
        
        return CoreMessage(
            topic="project.updated",
            content={
                "project_id": project_id,
                "update_type": update_type,
                "tasks": project_data["tasks"],
                "resources": project_data["resources"]
            },
            sender=self.agent_id
        )
        
    async def _handle_task_status(self, message: CoreMessage) -> Optional[CoreMessage]:
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
        
        return CoreMessage(
            topic="project.task.updated",
            content={
                "project_id": project_id,
                "task_id": task_id,
                "status": new_status,
                "tasks": updated_tasks,
                "resources": project_data["resources"]
            },
            sender=self.agent_id
        )
        
    async def _handle_agent_status(self, message: CoreMessage) -> Optional[CoreMessage]:
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
                
    async def _handle_resource_status(self, message: CoreMessage) -> Optional[CoreMessage]:
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
            return await self._handle_new_project(CoreMessage(
                topic="project.new",
                content=task["project_spec"],
                sender="system"
            ))
        elif task_type == "update_project":
            return await self._handle_project_update(CoreMessage(
                topic="project.update",
                content=task["update_spec"],
                sender="system"
            ))
        else:
            raise AgentError(f"Unknown task type: {task_type}")
        
    async def handle_error(self, error: Exception) -> None:
        """Handle agent errors."""
        self.logger.logger.error(f"Error in Director: {str(error)}")
        self.metrics.error_count.labels(
            agent_id=self.agent_id,
            agent_type=self.agent_type.value
        ).inc()

    async def _handle_task_creation(self, message: BaseMessage) -> BaseMessage:
        """Handle task creation request."""
        try:
            task = await self.task_service.create_task(message.content)  # Use task_service
            resources = await self.resource_service.get_resources()
            timeline = await self.planner_service.generate_timeline([task])
            
            return BaseMessage(
                type="task.created",
                content={
                    "task": task,
                    "resources": resources,
                    "timeline": timeline,
                    "action_type": "task_creation"
                },
                sender=self.agent_id
            )
        except Exception as e:
            raise AgentError(f"Failed to create task: {str(e)}")
        # Add any specific error handling logic here

    async def _publish_event(self, topic: str, content: dict) -> None:
        """Publish events using CoreMessage for pub/sub."""
        if self.message_broker:
            message = CoreMessage(
                topic=topic,
                content=content,
                sender=self.agent_id
            )
            await self.message_broker.publish(message)