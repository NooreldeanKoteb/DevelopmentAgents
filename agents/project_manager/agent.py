from dataclasses import dataclass
from typing import List, Dict, Any
from datetime import datetime

from agents.base.base_agent import BaseAgent
from agents.base.message import Message
from agents.project_manager.models import TaskData, ResourceData
from agents.project_manager.task_manager import TaskManager
from agents.project_manager.planner import ProjectPlanner
from agents.project_manager.resource_manager import ResourceManager
from agents.project_manager.action_analyzer import ActionAnalyzer
from agents.project_manager.priority import PriorityCalculator
from agents.project_manager.persistence import PersistenceManager

# Let's also make ProjectResponse a proper dataclass
@dataclass
class ProjectResponse:
    action_type: str
    tasks: List[Dict[str, Any]]
    timeline: Dict[str, Any]
    resources: List[Dict[str, Any]]
    priorities: List[str]

class ProjectManagerAgent(BaseAgent):
    def __init__(self) -> None:
        super().__init__()
        self.task_manager = TaskManager()
        self.planner = ProjectPlanner()
        self.resource_manager = ResourceManager()
        self.action_analyzer = ActionAnalyzer()
        self.priority_calculator = PriorityCalculator()
        self.persistence = PersistenceManager()

    async def process_message(self, message: Message) -> ProjectResponse:
        """Process incoming messages and coordinate project activities."""
        try:
            # Determine action type
            action_type = self.action_analyzer.determine_action_type(message)
            
            # Get current tasks
            tasks = await self.task_manager.get_tasks()
            
            # Calculate priorities for all tasks
            priorities = [
                self.priority_calculator.calculate_task_priority(task)
                for task in tasks
            ]
            
            # Generate timeline and allocate resources
            timeline = await self.planner.generate_timeline(tasks)
            resources = await self.resource_manager.allocate_resources(tasks)
            
            return ProjectResponse(
                action_type=action_type,
                tasks=tasks,
                timeline=timeline,
                resources=resources,
                priorities=priorities
            )
            
        except Exception as e:
            await self.handle_error(e)
            raise