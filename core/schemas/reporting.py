from datetime import datetime
from typing import Dict, Any, List, Optional
import json
from core.config import monitor_operation
from core.config.settings import get_settings
import redis.asyncio as redis

class SchemaViolationReporter:
    """Reports and tracks schema violations."""
    
    def __init__(self):
        self.redis = redis.from_url(get_settings().REDIS_URL)
    
    @monitor_operation(agent_type="schema", operation="report_violation")
    async def report_violation(
        self,
        error_id: str,
        schema_class: str,
        errors: List[Dict[str, Any]],
        data: Dict[str, Any]
    ) -> None:
        """Report a schema violation."""
        violation = {
            "error_id": error_id,
            "schema": schema_class,
            "errors": errors,
            "data": data,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Store violation report
        await self.redis.lpush("schema:violations", json.dumps(violation))
        
        # Update metrics
        await self.redis.hincrby("schema:stats", f"violations:{schema_class}", 1)
    
    async def get_violations(
        self,
        limit: int = 100,
        schema_class: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get recent schema violations."""
        violations = []
        all_violations = await self.redis.lrange("schema:violations", 0, limit - 1)
        
        for v in all_violations:
            violation = json.loads(v)
            if not schema_class or violation["schema"] == schema_class:
                violations.append(violation)
        
        return violations
    
    async def get_violation_stats(self) -> Dict[str, int]:
        """Get schema violation statistics."""
        return await self.redis.hgetall("schema:stats") 