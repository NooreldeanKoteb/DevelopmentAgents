from typing import Dict, Any, List
from datetime import datetime
from core.schemas import TaskPriority

def calculate_task_priority(task: Dict[str, Any]) -> str:
    """Calculate task priority based on various factors."""
    score = 0
    
    # Duration score (0-3 points)
    duration = task.get("estimated_duration", 0)
    if duration >= 5.0:
        score += 3
    elif duration >= 3.0:
        score += 2
    elif duration > 0:
        score += 1
        
    # Dependencies score (0-3 points)
    dependencies = task.get("dependencies", [])
    if len(dependencies) >= 3:
        score += 3
    elif len(dependencies) >= 1:
        score += 2
        
    # Business impact score (0-3 points)
    impact = task.get("business_impact", "low")
    if impact == "high":
        score += 3
    elif impact == "medium":
        score += 2
    elif impact == "low":
        score += 1
        
    # Status score (0-2 points)
    if task.get("status") == "blocked":
        score += 2
        
    # Convert score to priority (max score: 11)
    if score >= 10:
        return TaskPriority.HIGH.value
    elif score >= 6:
        return TaskPriority.MEDIUM.value
    else:
        return TaskPriority.LOW.value 
class PriorityCalculator:
    @staticmethod
    def calculate_deadline_score(minutes: int) -> float:
        """Calculate deadline score based on minutes until deadline."""
        if minutes <= 5:
            return 100
        elif minutes <= 15:
            return 90
        elif minutes <= 30:
            return 80
        elif minutes <= 60:
            return 70
        elif minutes <= 120:
            return 50
        return 30

    @staticmethod
    def calculate_dependency_score(task: Dict[str, Any]) -> float:
        """Calculate score based on task dependencies."""
        dependencies = task.get("dependencies", [])
        blocked_by = len(dependencies)
        blocking_others = task.get("blocking_count", 0)
        
        return min(100, (blocked_by * 20) + (blocking_others * 30))

    @staticmethod
    def calculate_impact_score(task: Dict[str, Any]) -> float:
        """Calculate score based on business impact."""
        impact_level = task.get("business_impact", "low").lower()
        return {
            "critical": 100,
            "high": 80,
            "medium": 60,
            "low": 40,
            "minimal": 20
        }.get(impact_level, 40)

    @staticmethod
    def calculate_resource_score(task: Dict[str, Any]) -> float:
        """Calculate score based on resource availability."""
        resource_status = task.get("resource_status", {})
        if resource_status.get("blocked", False):
            return 100
        if resource_status.get("limited", False):
            return 80
        return 40

    @staticmethod
    def score_to_priority(score: float) -> str:
        """Convert numerical score to priority level."""
        if score >= 95:
            return TaskPriority.CRITICAL.value
        elif score >= 70:
            return TaskPriority.HIGH.value
        elif score >= 40:
            return TaskPriority.MEDIUM.value
        return TaskPriority.LOW.value

    def calculate_task_priority(self, task: Dict[str, Any]) -> str:
        """Calculate overall task priority."""
        score = 0
        
        # Factor 1: Deadline proximity (30%)
        if "deadline" in task:
            minutes_until_deadline = (task["deadline"] - datetime.utcnow()).total_seconds() / 60
            deadline_score = self.calculate_deadline_score(minutes_until_deadline)
            score += deadline_score * 0.3
            
        # Factor 2: Dependencies (25%)
        dependency_score = self.calculate_dependency_score(task)
        score += dependency_score * 0.25
        
        # Factor 3: Business impact (25%)
        impact_score = self.calculate_impact_score(task)
        score += impact_score * 0.25
        
        # Factor 4: Resource availability (20%)
        resource_score = self.calculate_resource_score(task)
        score += resource_score * 0.20
        
        return self.score_to_priority(score) 