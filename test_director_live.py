import asyncio
import redis.asyncio as redis
from datetime import datetime
import os
from prometheus_client import REGISTRY, CollectorRegistry
from agents.director.agent import DirectorAgent
from agents.director.task_manager import TaskManager
from agents.director.resource_manager import ResourceManager
from agents.director.planner import ProjectPlanner
from agents.director.persistence import PersistenceManager
from core.messaging.message import Message
from agents.director.enums import BusinessImpact
from core.monitoring.metrics import CoreMetrics
from core.schemas.enums import Status, Priority
from agents.base.enums import AgentType, TaskType
from core.openai import OpenAIClient

# Configuration
REDIS_URL = "redis://localhost:6379/0"
OPENAI_API_KEY = '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'  # Get from environment variable

def clear_metrics():
    """Clear all prometheus metrics."""
    collectors = list(REGISTRY._collector_to_names.keys())
    print(f"Clearing {len(collectors)} collectors from registry...")
    for collector in collectors:
        REGISTRY.unregister(collector)
    print("Registry cleared")

async def setup_redis():
    """Setup Redis connection and clear test data."""
    print("Connecting to Redis...")
    client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
    try:
        await client.ping()
        print("Redis connection successful")
        await client.flushdb()
        print("Redis database cleared")
        return client
    except redis.ConnectionError:
        print("Error: Redis server is not running. Please start Redis first.")
        raise

async def cleanup_redis(redis_client):
    """Properly cleanup Redis connection."""
    try:
        await redis_client.flushdb()
        if hasattr(redis_client, 'connection_pool'):
            await redis_client.connection_pool.disconnect()
        await redis_client.aclose()
    except Exception as e:
        print(f"Error during Redis cleanup: {str(e)}")

async def print_project_plan(response):
    """Print detailed project plan information."""
    print("\nRaw Response:")
    print("=" * 50)
    print(response)
    
    if not response or not response.payload:
        print("\nError: No response or empty payload received")
        return

    payload = response.payload
    print("\nResponse Payload:")
    print("=" * 50)
    print(payload)
    
    print("\nProject Plan Details:")
    print("=" * 50)
    
    plan = payload.get('plan', {})
    
    # Print phases and tasks from the plan
    if "phases" in plan:
        print("\n📋 Phases:")
        for phase in plan["phases"]:
            print(f"\n📎 Phase: {phase['name']}")
            print(f"Description: {phase['description']}")
            
            if "tasks" in phase:
                print("\nTasks:")
                for task in phase["tasks"]:
                    print("\n  📌 Task Details:")
                    print(f"    ID: {task.get('id', 'Not specified')}")
                    print(f"    Name: {task['name']}")
                    print(f"    Agent: {task['assigned_to']}")
                    print(f"    Priority: {task['priority']}")
                    print(f"    Critical: {task.get('critical', 'Not specified')}")
                    print(f"    Risk Level: {task.get('risk_level', 'Not specified')}")
                    print(f"    Dependencies: {', '.join(task['dependencies']) if task['dependencies'] else 'None'}")
                    print(f"    Implementation Steps:")
                    for step in task['implementation_steps']:
                        print(f"      • {step}")
                    print(f"    Expected Outputs:")
                    for output in task.get('expected_outputs', []):
                        print(f"      • {output}")
                    print(f"    Completion Criteria:")
                    for criterion in task.get('completion_criteria', []):
                        print(f"      • {criterion}")
                    print(f"    Research Required: {task.get('research_required', False)}")
                    # print(f"    Required Specializations: {', '.join(task.get('required_specializations', []))}")
                    if 'requirements' in task:
                        print(f"    Requirements:")
                        for key, value in task['requirements'].items():
                            print(f"      • {key}: {value}")

    # Print dependencies
    if "dependencies" in plan:
        print("\n🔄 Dependencies:")
        print("=" * 30)
        for dep in plan["dependencies"]:
            print(f"  {dep['from']} → {dep['to']} ({dep['type']})")

    # Print critical path
    if "critical_path" in plan:
        print("\n⚡ Critical Path:")
        print("=" * 30)
        print(" → ".join(plan["critical_path"]))

    # Print risk assessment
    if "risk_assessment" in plan:
        print("\n⚠️ Risk Assessment:")
        print("=" * 30)
        risk = plan["risk_assessment"]
        print(f"Overall Risk Level: {risk['level']}")
        print("\nRisk Factors:")
        for factor in risk['factors']:
            print(f"  • {factor}")
        if 'high_risk_tasks' in risk:
            print("\nHigh Risk Tasks:")
            for task in risk['high_risk_tasks']:
                print(f"  • {task}")
        print("\nMitigation Strategies:")
        for strategy in risk['mitigations']:
            print(f"  • {strategy}")


    # Print created tasks
    if "tasks" in payload:
        print("\n📝 Created Tasks:")
        print("=" * 30)
        for task in payload["tasks"]:
            print(f"\nTask ID: {task.id}")
            print(f"Name: {task.name}")
            print(f"Priority: {task.priority}")
            print(f"Phase: {task.phase}")
            print(f"Created: {task.created_at}")

    # Print allocated resources
    if "resources" in payload:
        print("\n🔧 Allocated Resources:")
        print("=" * 30)
        for resource_id, resource in payload.get("resources", {}).items():
            print(f"\nResource: {resource_id}")
            print(f"Details: {resource}")

async def get_project_plan(planner: ProjectPlanner, project_spec: dict) -> dict:
    """Call OpenAI directly through planner to get project plan."""
    print("\nCalling OpenAI for project planning...")
    
    try:
        # Use the existing create_plan method
        response = await planner.create_plan(project_spec)
        
        print("\nRaw OpenAI Response:")
        print("=" * 80)
        print(response)
        
        return response
        
    except Exception as e:
        print(f"Error getting project plan from OpenAI: {str(e)}")
        raise

async def main():
    redis_client = None
    try:
        clear_metrics()
        redis_client = await setup_redis()
        
        print("\nInitializing services...")
        persistence = PersistenceManager(redis_client)
        task_manager = TaskManager(persistence)
        resource_manager = ResourceManager()
        
        print("Services initialized")
        
        print("\nCreating Director agent...")
        agent = DirectorAgent(
            name="director_agent",
            redis_client=redis_client,
            redis_url=REDIS_URL  # 
        )
        
        await agent.initialize()
        print("Agent initialized successfully")

        try:
            project_spec = {
                "id": "travel-app-1",
                "name": "social media travel app",
                # "description": """
                #     Create a social media travel app following features:
                #     - User authentication
                #     - CRUD operations for posts
                #     - Explore new places
                #     - Share your travel experiences
                #     - Follow other users
                #     - Like and comment on posts
                #     - Search for places
                #     - Create a community for travel enthusiasts
                #     """,
                "description": "Create a workout tracking app",
                "requirements": {
                    "language": "python",
                    "framework": "Flask",
                    "database": "DynamoDB",
                    "features": [
                        "create workout plan",
                        "track workout progress",
                        "create workout log",
                        "create workout history",
                        "create workout summary",
                        "create workout report",
                        "create workout analysis",
                        "create workout recommendation",
                        "keep track of reps, sets, and weights",
                        "keep track of calories burned",
                        "keep track of time spent",
                        "keep track of distance traveled",
                        "keep track of heart rate",
                        "keep track of sleep",
                        "keep track of nutrition",
                    ],
                },
                "priority": Priority.HIGH,
                "metadata": {},
                "tags": ["mobile", "social", "travel"]
            }

            # Get plan directly from OpenAI
            plan = await get_project_plan(agent.planner_service, project_spec)
            
            # Print the plan details
            await print_project_plan(Message(
                topic="project.plan",
                sender="planner",
                code="SUCCESS",
                message="Project plan generated successfully",
                recipient="director",
                type="task_creation",
                status=Status.COMPLETED,
                priority=Priority.HIGH,
                payload={"plan": plan}
            ))

        finally:
            try:
                print("\nCleaning up...")
                if 'agent' in locals():
                    print("Cleaning up agent...")
                    await agent.cleanup()
                    print("Agent cleanup complete")

                if redis_client:
                    print("\nClosing Redis connection...")
                    await cleanup_redis(redis_client)
                    print("Redis connection closed")
                    
                    # Add longer delay to ensure connections are closed
                    await asyncio.sleep(0.5)
            except Exception as e:
                print(f"Error during cleanup: {str(e)}")

    except Exception as e:
        print(f"\nError occurred: {str(e)}")
        import traceback
        traceback.print_exc()
        raise

if __name__ == "__main__":
    asyncio.run(main()) 