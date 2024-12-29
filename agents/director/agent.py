from typing import Dict, Any, Optional, List
from datetime import datetime
import asyncio
import uuid
import json

from agents.base import BaseAgent, AgentError  # Import base Message
from .enums import BusinessImpact
from .planner import ProjectPlanner
from .task_manager import TaskManager
from .resource_manager import ResourceManager
from agents.director.persistence import PersistenceManager
from redis import Redis
from core.openai import OpenAIClient
from agents.base.enums import AgentType
from core.schemas.enums import Status
from core.messaging.message import Message
from agents.base.topic_registry import TopicRegistry
from core.settings import settings

class DirectorAgent(BaseAgent):
    """Agent responsible for managing project resources and tasks."""    
    def __init__(
        self,
        name: str,
        task_service: TaskManager,
        resource_service: ResourceManager,
        redis_client: Optional[Redis] = None,
        redis_url: Optional[str] = None
    ):
        """Initialize the Director agent."""
        super().__init__(
            name=name,
            agent_type=AgentType.DIRECTOR,
            redis_client=redis_client,
            redis_url=redis_url
        )

        self.openai = OpenAIClient()  # Initialize OpenAI client here
        self.system_status = Status.ACTIVE
        self.agent_heartbeats: Dict[str, datetime] = {}  # Track agent heartbeats

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
            topics = TopicRegistry.get_agent_topics(AgentType.DIRECTOR)
            
            for topic in topics:
                await self.message_broker.subscribe(
                    topic=topic,
                    callback=self.process_message  # Use process_message as the callback
                )
        
    async def _handle_message_type(self, message: Message) -> Any:
        """Handle different types of project management messages."""
        # Get subscription details from registry
        subscription = TopicRegistry.get_subscription(message.topic)
        if not subscription:
            raise AgentError(f"Unsupported topic: {message.topic}")

        # Map topics to handlers
        topic_handlers = {
            # Project Management
            "director.project.create": self._handle_new_project,
            "director.project.update": self._handle_project_update,
            "director.project.delete": self._handle_project_deletion,
            
            # Task Management
            "director.task.create": self._handle_task_creation,
            "director.task.update": self._handle_task_status,
            "director.task.delete": self._handle_task_deletion,
            "director.task.assign": self._handle_task_assignment,
            
            # Status Updates
            "task.status": self._handle_task_status,
            "agent.status": self._handle_agent_status,
            "resource.status": self._handle_resource_status,
            
            # Global Topics
            "system.status": self._handle_system_status,
            "system.error": self._handle_system_error,
            "agent.heartbeat": self._handle_heartbeat
        }
        
        handler = topic_handlers.get(message.topic)
        if not handler:
            raise AgentError(f"No handler for topic: {message.topic}")
        
        return await handler(message)
        
    async def _handle_new_project(self, message: Message) -> Message:
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
        
        return Message(
            topic="project.created",
            content={
                "project_id": project_spec['id'],
                "plan": plan,
                "tasks": tasks,
                "resources": resources
            },
            sender=self.agent_id
        )
        
    async def _handle_project_update(self, message: Message) -> Optional[Message]:
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
        
        return Message(
            topic="project.updated",
            content={
                "project_id": project_id,
                "update_type": update_type,
                "tasks": project_data["tasks"],
                "resources": project_data["resources"]
            },
            sender=self.agent_id
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
        if new_status in [Status.COMPLETED, Status.FAILED]:
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
            sender=self.agent_id
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
        # TODO: Implement error handling    
        self.logger.logger.error(f"Error in Director: {str(error)}")
        self.metrics.error_count.labels(
            agent_id=self.agent_id,
            agent_type=self.agent_type.value
        ).inc()

    async def _handle_task_creation(self, message: Message) -> Message:
        """Handle task creation request."""
        try:
            task = await self.task_service.create_task(message.content)  # Use task_service
            resources = await self.resource_service.get_resources()
            timeline = await self.planner_service.generate_timeline([task])
            
            return Message(
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
        """Publish events using Message for pub/sub."""
        if self.message_broker:
            message = Message(
                topic=topic,
                content=content,
                sender=self.agent_id
            )
            await self.message_broker.publish(message)

    async def _handle_project_deletion(self, message: Message) -> Optional[Message]:
        """Handle project deletion request."""
        project_id = message.content["project_id"]
        
        # Delete project data
        await self.memory.delete(f"project:{project_id}")
        
        # Release resources
        await self.resource_service.release_project_resources(project_id)
        
        return Message(
            topic="project.deleted",
            content={"project_id": project_id},
            sender=self.agent_id
        )

    async def _handle_task_deletion(self, message: Message) -> Optional[Message]:
        """Handle task deletion request."""
        task_id = message.content["task_id"]
        project_id = message.content["project_id"]
        
        project_data = await self.recall_from_memory(f"project:{project_id}")
        if not project_data:
            raise AgentError(f"Project {project_id} not found")
        
        # Remove task and update project
        updated_tasks = await self.task_service.delete_task(
            project_data["tasks"],
            task_id
        )
        project_data["tasks"] = updated_tasks
        
        # Update resources
        resources = await self.resource_service.reallocate_resources(
            updated_tasks,
            project_data["resources"]
        )
        project_data["resources"] = resources
        
        await self.save_to_memory(f"project:{project_id}", project_data)
        
        return Message(
            topic="task.deleted",
            content={
                "project_id": project_id,
                "task_id": task_id,
                "tasks": updated_tasks,
                "resources": resources
            },
            sender=self.agent_id
        )

    async def _handle_task_assignment(self, message: Message) -> Optional[Message]:
        """Handle task assignment request."""
        task_id = message.content["task_id"]
        agent_id = message.content["agent_id"]
        project_id = message.content["project_id"]
        
        project_data = await self.recall_from_memory(f"project:{project_id}")
        if not project_data:
            raise AgentError(f"Project {project_id} not found")
        
        # Update task assignment
        updated_tasks = await self.task_service.assign_task(
            project_data["tasks"],
            task_id,
            agent_id
        )
        project_data["tasks"] = updated_tasks
        
        await self.save_to_memory(f"project:{project_id}", project_data)
        
        return Message(
            topic="task.assigned",
            content={
                "project_id": project_id,
                "task_id": task_id,
                "agent_id": agent_id,
                "tasks": updated_tasks
            },
            sender=self.agent_id
        )

    async def _handle_system_status(self, message: Message) -> None:
        """Handle system status updates."""
        status = message.content["status"]
        self.system_status = status
        await self._check_system_impact(status)

    async def _handle_system_error(self, message: Message) -> None:
        """Handle system error notifications."""
        error = message.content["error"]
        await self.handle_error(error)

    async def _handle_heartbeat(self, message: Message) -> None:
        """Handle agent heartbeat messages."""
        agent_id = message.content["agent_id"]
        timestamp = message.content["timestamp"]
        # Update agent heartbeat tracking
        self.agent_heartbeats[agent_id] = timestamp
        await self._check_agent_health(agent_id)

    async def _check_system_impact(self, status: str) -> None:
        """Check if system status impacts any projects."""
        if status in ["error", "maintenance"]:
            projects = await self._get_active_projects()
            for project_id in projects:
                await self._handle_project_system_impact(project_id, status)

    async def _check_agent_health(self, agent_id: str) -> None:
        """Check agent health based on heartbeat."""
        last_heartbeat = self.agent_heartbeats.get(agent_id)
        if last_heartbeat:
            # Check if heartbeat is too old
            if (datetime.now() - last_heartbeat).seconds > settings.HEARTBEAT_TIMEOUT:
                await self._handle_agent_status(Message(
                    topic="agent.status",
                    content={
                        "agent_id": agent_id,
                        "status": "offline"
                    },
                    sender="system"
                ))

    async def _handle_project_system_impact(self, project_id: str, status: str) -> None:
        """Handle system status impact on a project.
        
        Args:
            project_id: The ID of the project to check
            status: The system status affecting the project
        """
        project_data = await self.recall_from_memory(f"project:{project_id}")
        if not project_data:
            return

        if status == "error":
            # Pause active tasks
            updated_tasks = await self.task_service.pause_active_tasks(
                project_data["tasks"],
                reason=f"System error: {status}"
            )
            project_data["tasks"] = updated_tasks

        elif status == "maintenance":
            # Schedule tasks around maintenance
            updated_tasks = await self.task_service.reschedule_tasks(
                project_data["tasks"],
                delay_minutes=30  # Configurable delay
            )
            project_data["tasks"] = updated_tasks

        # Update project data
        await self.save_to_memory(f"project:{project_id}", project_data)

        # Notify relevant agents
        await self._publish_event(
            topic="project.status.update",
            content={
                "project_id": project_id,
                "status": status,
                "tasks": project_data["tasks"]
            }
        )