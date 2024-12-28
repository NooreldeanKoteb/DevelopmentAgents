from typing import Dict, Any, List, Optional, TYPE_CHECKING
from datetime import datetime, timedelta
import asyncio
import yaml
from pathlib import Path
import json
from openai import OpenAIError

from core.openai import OpenAIClient
from core.schemas import TaskSchema, TaskStatus, TaskPriority
from .errors import PlanningError

# Use TYPE_CHECKING for imports only needed for type hints
if TYPE_CHECKING:
    from .agent import ProjectManagerAgent

class ProjectPlanner:
    """Handles project planning and task organization."""
    
    def __init__(self, agent=None):
        """Initialize the project planner.
        
        Args:
            agent: The agent instance this planner is associated with
        """
        self.agent = agent
        self.prompts = self._load_prompts()
        
    def _load_prompts(self) -> Dict[str, Any]:
        """Load prompts from YAML file."""
        prompt_path = Path("prompts/project_manager/planning.yaml")
        try:
            with open(prompt_path) as f:
                return yaml.safe_load(f)
        except Exception as e:
            raise PlanningError(f"Failed to load prompts: {str(e)}")
        
    async def create_plan(self, project_spec: Dict[str, Any]) -> Dict[str, Any]:
        """Create a project plan based on the project specification."""
        try:
            # Format the prompt with project details
            prompt = await self._format_planning_prompt(project_spec)
            
            # Get response from OpenAI using the agent's client
            response = await self.agent.openai.get_completion(prompt)
            
            # Parse and validate the response
            plan = await self._parse_plan_response(response.content)
            
            # Store the plan
            await self._store_plan(project_spec["name"], plan)
            
            return plan
            
        except OpenAIError as e:
            raise PlanningError(f"OpenAI error while creating plan: {str(e)}")
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
            
    async def _parse_plan_response(self, response) -> Dict[str, Any]:
        """Parse and validate the plan response from OpenAI."""
        try:
            # Check if response is already a dict
            if isinstance(response, dict):
                plan_data = response
            else:
                # Parse JSON string
                plan_data = json.loads(response)
                
            # Validate required fields
            required_fields = {"phases", "dependencies", "estimated_duration", "critical_path", "risk_assessment"}
            missing_fields = required_fields - set(plan_data.keys())
            
            if missing_fields:
                raise PlanningError(f"Missing required fields in plan: {missing_fields}")
                
            # Validate phases structure
            for phase in plan_data["phases"]:
                if not isinstance(phase.get("tasks"), list):
                    raise PlanningError(f"Invalid tasks format in phase: {phase.get('name')}")
                    
                for task in phase["tasks"]:
                    required_task_fields = {
                        "name", "description", "estimated_duration",
                        "dependencies", "required_skills", "resources"
                    }
                    missing_task_fields = required_task_fields - set(task.keys())
                    
                    if missing_task_fields:
                        raise PlanningError(
                            f"Missing required fields in task {task.get('name')}: {missing_task_fields}"
                        )
                        
            return plan_data
            
        except json.JSONDecodeError as e:
            raise PlanningError(f"Invalid JSON format: {str(e)}")
        except Exception as e:
            raise PlanningError(f"Error validating plan: {str(e)}")

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

    async def _format_planning_prompt(self, project_spec: Dict[str, Any]) -> str:
        """Format the planning prompt using the YAML template."""
        try:
            create_plan = self.prompts['create_plan']
            return (
                f"{create_plan['system']}\n\n"
                f"{create_plan['prompt'].format(project=project_spec)}"
            )
        except KeyError as e:
            raise PlanningError(f"Missing required project field: {str(e)}")
        except Exception as e:
            raise PlanningError(f"Error formatting prompt: {str(e)}")

    async def _store_plan(self, project_name: str, plan: Dict[str, Any]) -> None:
        """Store the project plan in memory."""
        try:
            plan_key = f"plan:{project_name}"
            
            # Convert any TaskSchema objects to dictionaries
            serialized_plan = {
                "plan": {
                    **plan,
                    "tasks": [
                        task.to_dict() if hasattr(task, 'to_dict') else task 
                        for task in plan.get("tasks", [])
                    ]
                },
                "created_at": datetime.now().isoformat(),
                "status": "active"
            }
            
            await self.agent.save_to_memory(
                key=plan_key,
                value=serialized_plan
            )
            
        except Exception as e:
            raise PlanningError(f"Failed to store plan: {str(e)}")