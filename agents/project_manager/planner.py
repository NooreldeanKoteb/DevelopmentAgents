from typing import List, Dict, Any
from datetime import datetime, timedelta

import networkx as nx

from agents.project_manager.models import TaskData

class ProjectPlanner:
    def __init__(self) -> None:
        self.current_timeline: Dict[str, Any] = {}

    async def generate_timeline(self, tasks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate a project timeline based on tasks."""
        timeline = {
            "start_date": datetime.utcnow(),
            "end_date": None,
            "milestones": [],
            "critical_path": [],
            "phases": []
        }

        if not tasks:
            return timeline

        # Create a directed graph for task dependencies
        graph = nx.DiGraph()
        for task in tasks:
            graph.add_node(task["id"], **task)
            for dep in task.get("dependencies", []):
                graph.add_edge(dep, task["id"])

        # Calculate critical path using network analysis
        try:
            critical_path = nx.dag_longest_path(graph, weight="estimated_duration")
            timeline["critical_path"] = [graph.nodes[task_id] for task_id in critical_path]
        except nx.NetworkXError:
            timeline["critical_path"] = []

        # Sort tasks by dependencies
        sorted_tasks = list(nx.topological_sort(graph))
        sorted_task_data = [graph.nodes[task_id] for task_id in sorted_tasks]
        
        # Calculate phase distribution
        phases = self._distribute_into_phases(sorted_task_data)
        timeline["phases"] = phases

        # Generate milestones
        timeline["milestones"] = self._generate_milestones(phases)

        # Calculate end date based on critical path
        if timeline["critical_path"]:
            total_duration = sum(task["estimated_duration"] for task in timeline["critical_path"])
            timeline["end_date"] = timeline["start_date"] + timedelta(hours=total_duration)

        return timeline

    def _distribute_into_phases(self, tasks: List[Dict[str, Any]]) -> List[List[Dict[str, Any]]]:
        """Distribute tasks into phases based on dependencies and resources."""
        phases = []
        current_phase = []
        
        for task in tasks:
            if len(current_phase) >= 5:  # arbitrary limit for demonstration
                phases.append(current_phase)
                current_phase = []
            current_phase.append(task)
            
        if current_phase:
            phases.append(current_phase)
            
        return phases

    def _generate_milestones(self, phases: List[List[Dict[str, Any]]]) -> List[Dict[str, Any]]:
        """Generate project milestones based on phases."""
        milestones = []
        current_date = datetime.utcnow()
        
        for i, phase in enumerate(phases):
            milestone = {
                "name": f"Phase {i + 1} Complete",
                "date": current_date + timedelta(hours=i * 4),  # 4-hour phases
                "deliverables": [task["name"] for task in phase]
            }
            milestones.append(milestone)
            
        return milestones

    def _calculate_phase_duration(self, phase: List[Dict[str, Any]]) -> float:
        """Calculate the duration of a phase based on parallel execution."""
        if not phase:
            return 0.0
            
        # Create a small graph for the phase
        graph = nx.DiGraph()
        for task in phase:
            graph.add_node(task["id"], duration=task["estimated_duration"])
            for dep in task.get("dependencies", []):
                if any(t["id"] == dep for t in phase):  # only consider in-phase dependencies
                    graph.add_edge(dep, task["id"])
                    
        # Find the longest path in this phase
        try:
            path_length = nx.dag_longest_path_length(graph, weight="duration")
            return path_length
        except (nx.NetworkXError, nx.NetworkXNoPath):
            # If no dependencies, return max duration of any task
            return max(task["estimated_duration"] for task in phase)