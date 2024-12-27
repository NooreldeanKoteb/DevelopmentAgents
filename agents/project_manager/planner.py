from typing import Dict, Any, List, Optional, TYPE_CHECKING
from datetime import datetime, timedelta
import asyncio
import yaml
from pathlib import Path

from core.openai import OpenAIClient
from core.schemas import TaskSchema, TaskStatus, TaskPriority
from .errors import PlanningError

# Use TYPE_CHECKING for imports only needed for type hints
if TYPE_CHECKING:
    from .agent import ProjectManagerAgent

class ProjectPlanner:
    """Handles project planning and task organization."""
    
    def __init__(self, agent: 'ProjectManagerAgent'):
        """Initialize with reference to parent agent."""
        self.agent = agent
        self.prompts = self._load_prompts()
        
    def _load_prompts(self) -> Dict[str, Any]:
        """Load prompts from YAML file."""
        prompt_path = Path("prompts/project_manager/planning.yaml")
        with open(prompt_path, 'r') as f:
            return yaml.safe_load(f)
        
    async def create_plan(self, project_spec: Dict[str, Any]) -> Dict[str, Any]:
        """Create a project plan from specifications."""
        try:
            # Get prompts
            system_prompt = self.prompts["create_plan"]["system"]
            user_prompt = self.prompts["create_plan"]["prompt"].format(
                name=project_spec["name"],
                description=project_spec["description"],
                requirements=project_spec["requirements"]
            )
            
            # Use agent's OpenAI client instead of own instance
            response = await self.agent.openai.get_completion(
                user_prompt,
                system_prompt=system_prompt
            )
            
            # Parse and validate plan
            plan = self._parse_plan_response(response.content)
            
            return {
                "id": project_spec["id"],
                "name": project_spec["name"],
                "phases": plan["phases"],
                "dependencies": plan["dependencies"],
                "estimated_duration": plan["estimated_duration"],
                "critical_path": plan["critical_path"],
                "risk_assessment": plan["risk_assessment"],
                "created_at": datetime.now().isoformat(),
                "status": "created"
            }
            
        except Exception as e:
            raise PlanningError(f"Failed to create plan: {str(e)}")
            
    async def update_plan(
        self,
        current_plan: Dict[str, Any],
        changes: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update existing project plan."""
        try:
            # Get prompts
            system_prompt = self.prompts["update_plan"]["system"]
            user_prompt = self.prompts["update_plan"]["prompt"].format(
                current_plan=current_plan,
                changes=changes
            )
            
            # Generate update using OpenAI
            response = await self.agent.openai.get_completion(
                user_prompt,
                system_prompt=system_prompt
            )
            
            # Parse and validate updated plan
            updated_plan = self._parse_plan_response(response.content)
            
            return {
                **current_plan,
                "phases": updated_plan["phases"],
                "dependencies": updated_plan["dependencies"],
                "estimated_duration": updated_plan["estimated_duration"],
                "critical_path": updated_plan["critical_path"],
                "impact_assessment": updated_plan["impact_assessment"],
                "updated_at": datetime.now().isoformat(),
                "status": "updated"
            }
            
        except Exception as e:
            raise PlanningError(f"Failed to update plan: {str(e)}")
            
    def _parse_plan_response(self, response: str) -> Dict[str, Any]:
        """Parse and validate OpenAI response."""
        # Implementation would parse JSON and validate structure
        # For now, we'll assume response is already in correct format
        return response

    async def generate_timeline(self, tasks: List[TaskSchema]) -> Dict[str, Any]:
        """Generate project timeline from tasks."""
        timeline = {
            "phases": self._distribute_into_phases(tasks),
            "milestones": self._generate_milestones(tasks),
            "estimated_duration": self._calculate_total_duration(tasks)
        }
        return timeline

    def _distribute_into_phases(self, tasks: List[TaskSchema]) -> List[Dict[str, Any]]:
        """Distribute tasks into phases based on dependencies."""
        phases = []
        # Group tasks by phase
        phase_groups = {}
        for task in tasks:
            if task.phase not in phase_groups:
                phase_groups[task.phase] = []
            phase_groups[task.phase].append(task)
        
        # Convert to list of phase dictionaries
        for phase_name, phase_tasks in phase_groups.items():
            phases.append({
                "name": phase_name,
                "tasks": [t.id for t in phase_tasks],
                "duration": sum(float(t.estimated_duration) for t in phase_tasks)
            })
        return phases

    def _generate_milestones(self, tasks: List[TaskSchema]) -> List[Dict[str, Any]]:
        """Generate project milestones from tasks."""
        milestones = []
        for task in tasks:
            if not task.dependencies:  # Start milestone
                milestones.append({
                    "name": f"Start {task.name}",
                    "task_id": task.id,
                    "type": "start"
                })
        return milestones

    def _calculate_total_duration(self, tasks: List[TaskSchema]) -> float:
        """Calculate total project duration."""
        return sum(float(task.estimated_duration) for task in tasks)