from typing import List, Dict, Any, Optional
from datetime import datetime
import heapq
from dataclasses import dataclass
from prometheus_client import Counter, Gauge
from agents.project_manager.persistence import PersistenceManager

@dataclass
class AgentLoad:
    agent_id: str
    current_load: float
    capacity: float
    specialization: List[str]
    performance_score: float

class ResourceManager:
    def __init__(self) -> None:
        self.persistence = PersistenceManager()
        self.load_threshold = 0.8  # 80% capacity
        
        # Metrics
        self.allocation_counter = Counter(
            'resource_allocations_total', 
            'Total number of resource allocations'
        )
        self.agent_load_gauge = Gauge(
            'agent_load', 
            'Current load of agents',
            ['agent_id']
        )

    async def allocate_resources(self, tasks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Allocate resources using load balancing."""
        allocations = []
        agent_loads = await self._get_agent_loads()
        
        for task in tasks:
            best_agent = await self._find_optimal_agent(task, agent_loads)
            
            if best_agent:
                allocation = {
                    "task_id": task["id"],
                    "agent_id": best_agent.agent_id,
                    "allocated_at": datetime.utcnow(),
                    "estimated_hours": task["estimated_duration"],
                    "status": "allocated"
                }
                
                # Update agent load
                self._update_agent_load(best_agent, task["estimated_duration"])
                allocations.append(allocation)
                
                # Update metrics
                self.allocation_counter.inc()
                self.agent_load_gauge.labels(agent_id=best_agent.agent_id).set(best_agent.current_load)
                
        return allocations

    async def _find_optimal_agent(self, task: Dict[str, Any], agent_loads: List[AgentLoad]) -> Optional[AgentLoad]:
        """Find the optimal agent using multiple criteria."""
        candidates = []
        required_skills = set(task.get("required_skills", []))
        
        for agent in agent_loads:
            if agent.current_load >= self.load_threshold:
                continue
                
            agent_skills = set(agent.specialization)
            skill_match_score = len(required_skills & agent_skills) / len(required_skills) if required_skills else 1.0
            
            # Calculate weighted score
            score = (
                0.4 * (1 - agent.current_load) +  # Load balance
                0.3 * skill_match_score +         # Skill match
                0.3 * agent.performance_score     # Historical performance
            )
            
            heapq.heappush(candidates, (-score, agent))  # Negative score for max-heap
            
        return candidates[0][1] if candidates else None

    async def _get_agent_loads(self) -> List[AgentLoad]:
        """Get current load information for all agents."""
        agents = await self.persistence.get_all_resources()
        return [
            AgentLoad(
                agent_id=agent["id"],
                current_load=agent["current_load"],
                capacity=agent.get("capacity", 1.0),
                specialization=agent.get("capabilities", []),
                performance_score=agent.get("performance_score", 0.5)
            )
            for agent in agents
        ]

    def _find_best_agent(self, task: Dict[str, Any]) -> str:
        """Find the most suitable agent for a task."""
        # Placeholder - implement actual agent selection logic
        return "default_agent"

    async def register_agent(self, agent_id: str, capabilities: Dict[str, Any]) -> None:
        """Register a new agent with their capabilities."""
        agent_data = {
            "capabilities": capabilities,
            "current_load": 0,
            "last_updated": datetime.utcnow().isoformat()
        }
        await self.persistence.save_resource(agent_id, agent_data)

    async def update_agent_status(self, agent_id: str, status_update: Dict[str, Any]) -> None:
        """Update an agent's status and availability."""
        agent_data = await self.persistence.get_resource(agent_id)
        if not agent_data:
            raise ValueError(f"Agent {agent_id} not found")
            
        agent_data.update(status_update)
        agent_data["last_updated"] = datetime.utcnow().isoformat()
        await self.persistence.save_resource(agent_id, agent_data) 