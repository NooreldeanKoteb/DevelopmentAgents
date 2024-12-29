from typing import Dict, Any
from datetime import datetime
from core.schemas import TaskSchema
from core.schemas.enums import BusinessImpact
from core.schemas.enums import Priority

def calculate_priority_score(task: TaskSchema) -> float:
    """Calculate priority score based on task attributes."""
    priority_weights = {
        Priority.HIGH: 5.0,
        Priority.MEDIUM: 3.0,
        Priority.LOW: 1.0
    }
    
    impact_weights = {
        BusinessImpact.HIGH: 3.0,
        BusinessImpact.MEDIUM: 2.0,
        BusinessImpact.LOW: 1.0
    }
    
    return (priority_weights[task.priority] * 
            impact_weights[task.business_impact])

def calculate_task_priority(task: TaskSchema) -> Priority:
    """Calculate overall task priority."""
    score = calculate_priority_score(task)
    
    if score >= 8.0:
        return Priority.HIGH
    elif score >= 4.0:
        return Priority.MEDIUM
    else:
        return Priority.LOW

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
    def score_to_priority(score: float) -> Priority:
        """Convert numerical score to priority level."""
        if score >= 95:
            return Priority.HIGH
        elif score >= 70:
            return Priority.HIGH
        elif score >= 40:
            return Priority.MEDIUM
        return Priority.LOW

    def calculate_priority(self, task: Dict[str, Any]) -> Priority:
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