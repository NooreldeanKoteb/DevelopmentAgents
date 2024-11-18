from typing import List, Dict, Any, Set
from datetime import datetime, timedelta
from dataclasses import dataclass
from collections import defaultdict
import networkx as nx

@dataclass
class PlanningMetrics:
    total_duration: float
    resource_utilization: float
    critical_path_length: int
    risk_score: float

class ProjectPlanner:
    def __init__(self) -> None:
        self.graph = nx.DiGraph()
        self.metrics = defaultdict(float)

    async def generate_timeline(self, tasks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate an optimized project timeline using network analysis."""
        self._build_dependency_graph(tasks)
        
        timeline = {
            "start_date": datetime.utcnow(),
            "end_date": None,
            "milestones": [],
            "critical_path": [],
            "phases": [],
            "risk_factors": [],
            "metrics": {}
        }

        # Calculate critical path using network analysis
        critical_path = self._calculate_critical_path_network()
        timeline["critical_path"] = critical_path

        # Generate optimized phases using resource constraints
        phases = self._generate_optimized_phases(tasks)
        timeline["phases"] = phases

        # Calculate end date using PERT estimation
        end_date = self._calculate_pert_completion_date(tasks)
        timeline["end_date"] = end_date

        # Generate risk-aware milestones
        timeline["milestones"] = self._generate_risk_aware_milestones(phases)
        
        # Calculate and store metrics
        timeline["metrics"] = self._calculate_planning_metrics()

        return timeline

    def _build_dependency_graph(self, tasks: List[Dict[str, Any]]) -> None:
        """Build a directed graph of task dependencies."""
        self.graph.clear()
        for task in tasks:
            self.graph.add_node(task["id"], **task)
            for dep in task.get("dependencies", []):
                self.graph.add_edge(dep, task["id"])

    def _calculate_critical_path_network(self) -> List[Dict[str, Any]]:
        """Calculate critical path using network analysis."""
        try:
            critical_path = nx.dag_longest_path(self.graph, weight="estimated_duration")
            return [self.graph.nodes[task_id] for task_id in critical_path]
        except nx.NetworkXError:
            return []

    def _generate_optimized_phases(self, tasks: List[Dict[str, Any]]) -> List[List[Dict[str, Any]]]:
        """Generate optimized phases using resource leveling."""
        phases = []
        remaining_tasks = tasks.copy()
        
        while remaining_tasks:
            phase_tasks = []
            resource_usage = defaultdict(float)
            
            for task in remaining_tasks[:]:
                if self._can_add_to_phase(task, resource_usage):
                    phase_tasks.append(task)
                    remaining_tasks.remove(task)
                    self._update_resource_usage(task, resource_usage)
                    
            if phase_tasks:
                phases.append(phase_tasks)
                
        return phases

    def _calculate_pert_completion_date(self, tasks: List[Dict[str, Any]]) -> datetime:
        """Calculate completion date using PERT estimation."""
        start_date = datetime.utcnow()
        
        # PERT = (Optimistic + 4x Most Likely + Pessimistic) / 6
        total_duration = sum(
            (task.get("optimistic_duration", task["estimated_duration"]) + 
             4 * task["estimated_duration"] + 
             task.get("pessimistic_duration", task["estimated_duration"] * 1.5)) / 6
            for task in tasks
        )
        
        return start_date + timedelta(hours=total_duration)

    def _calculate_planning_metrics(self) -> PlanningMetrics:
        """Calculate planning metrics."""
        return PlanningMetrics(
            total_duration=self._calculate_total_duration(),
            resource_utilization=self._calculate_resource_utilization(),
            critical_path_length=len(self._calculate_critical_path_network()),
            risk_score=self._calculate_risk_score()
        )

    def _can_add_to_phase(self, task: Dict[str, Any], resource_usage: Dict[str, float]) -> bool:
        """Check if a task can be added to a phase."""
        return sum(resource_usage.values()) + task["estimated_duration"] <= 8

    def _update_resource_usage(self, task: Dict[str, Any], resource_usage: Dict[str, float]) -> None:
        """Update resource usage for a task."""
        for resource in task["resources"]:
            resource_usage[resource] += task["estimated_duration"]

    def _calculate_total_duration(self) -> float:
        """Calculate total duration of the project."""
        return sum(task["estimated_duration"] for task in self._calculate_critical_path_network())

    def _calculate_resource_utilization(self) -> float:
        """Calculate resource utilization of the project."""
        total_resources = sum(self.graph.nodes[task_id]["resources"] for task_id in self.graph.nodes)
        return sum(self.metrics.values()) / total_resources

    def _calculate_risk_score(self) -> float:
        """Calculate risk score of the project."""
        return sum(self.metrics.values()) / len(self.graph.nodes)

    def _generate_risk_aware_milestones(self, phases: List[List[Dict[str, Any]]]) -> List[Dict[str, Any]]:
        """Generate risk-aware milestones based on phases."""
        milestones = []
        current_date = datetime.utcnow()
        
        for i, phase in enumerate(phases):
            milestone = {
                "name": f"Phase {i + 1} Complete",
                "date": current_date + timedelta(days=i * 14),  # arbitrary spacing
                "deliverables": [task["name"] for task in phase]
            }
            milestones.append(milestone)
            
        return milestones 