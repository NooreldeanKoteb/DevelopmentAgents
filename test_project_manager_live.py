import asyncio
import redis.asyncio as redis
from datetime import datetime
from prometheus_client import REGISTRY, CollectorRegistry
from agents.project_manager.agent import ProjectManagerAgent
from agents.project_manager.task_manager import TaskManager
from agents.project_manager.resource_manager import ResourceManager
from agents.project_manager.planner import ProjectPlanner
from agents.project_manager.persistence import PersistenceManager
from core.messaging.message import Message
from core.schemas.enums import TaskPriority, BusinessImpact
from core.monitoring.metrics import CoreMetrics

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
        await redis_client.aclose()  # Use aclose() instead of close()
        # Give event loop time to process cleanup
        await asyncio.sleep(0.1)
    except Exception as e:
        print(f"Error during Redis cleanup: {str(e)}")

async def print_project_plan(response):
    """Print detailed project plan information."""
    print("\nRaw Response:")
    print("=" * 50)
    print(response)
    
    if not response or not response.content:
        print("\nError: No response or empty content received")
        return

    content = response.content
    print("\nResponse Content:")
    print("=" * 50)
    print(content)
    
    print("\nProject Plan Details:")
    print("=" * 50)
    
    plan = content.get('plan', {})
    
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
                    print(f"    Name: {task['name']}")
                    print(f"    Description: {task['description']}")
                    print(f"    Duration: {task['estimated_duration']} days")
                    print(f"    Priority: {task['priority']}")
                    print(f"    Business Impact: {task['business_impact']}")
                    print(f"    Status: {task['status']}")
                    print(f"    Critical: {task.get('critical', 'Not specified')}")
                    print(f"    Risk Level: {task.get('risk_level', 'Not specified')}")
                    print(f"    Dependencies: {', '.join(task['dependencies']) if task['dependencies'] else 'None'}")
                    print(f"    Required Skills: {', '.join(task['required_skills'])}")
                    print(f"    Resources: {', '.join(task['resources'])}")

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

    # Print overall duration
    if "estimated_duration" in plan:
        print(f"\n⏱️ Total Estimated Duration: {plan['estimated_duration']} days")

    # Print created tasks
    if "tasks" in content:
        print("\n📝 Created Tasks:")
        print("=" * 30)
        for task in content["tasks"]:
            print(f"\nTask ID: {task.id}")
            print(f"Name: {task.name}")
            print(f"Status: {task.status}")
            print(f"Priority: {task.priority}")
            print(f"Business Impact: {task.business_impact}")
            print(f"Phase: {task.phase}")
            print(f"Created: {task.created_at}")

    # Print allocated resources
    if "resources" in content:
        print("\n🔧 Allocated Resources:")
        print("=" * 30)
        for resource_id, resource in content.get("resources", {}).items():
            print(f"\nResource: {resource_id}")
            print(f"Details: {resource}")

async def main():
    try:
        clear_metrics()
        redis_client = await setup_redis()
        
        print("\nInitializing services...")
        # Initialize services with Redis client
        persistence = PersistenceManager(redis_client)
        task_manager = TaskManager(persistence)
        resource_manager = ResourceManager()
        
        print("Services initialized")
        
        print("\nCreating Project Manager agent...")
        agent = ProjectManagerAgent(
            name="Project Manager",
            agent_type="project_manager",
            task_service=task_manager,
            resource_service=resource_manager,
            planner_service=None,  # Set to None initially
            redis_client=redis_client
        )
        
        # Initialize planner with agent reference after agent creation
        planner = ProjectPlanner(agent=agent)
        agent.planner_service = planner  # Set planner after initialization
        
        # Initialize the agent
        await agent.initialize()
        print("Agent initialized successfully")

        try:
            project_spec = {
                "id": "travel-app-1",  # Add project ID
                "name": "social media travel app",
                "description": """
                    Create a social media travel app following features:
                    - User authentication
                    - CRUD operations for posts
                    - Explore new places
                    - Share your travel experiences
                    - Follow other users
                    - Like and comment on posts
                    - Search for places
                    - Create a community for travel enthusiasts
                    """,
                "requirements": {
                    "language": "node.js",
                    "framework": "React Native",
                    "database": "MongoDB",
                    "features": [
                        "authentication",
                        "crud",
                        "file_upload",
                        "rate_limiting",
                        "documentation",
                        "explore_new_places",
                        "share_travel_experiences",
                        "follow_other_users",
                        "like_and_comment_on_posts",
                        "search_for_places",
                        "create_a_community_for_travel_enthusiasts"
                    ]
                },
                "priority": TaskPriority.HIGH.value,  # Use .value for enum
                "business_impact": BusinessImpact.HIGH.value,  # Use .value for enum
                "estimated_duration": 14.0  # days
            }

            print("\nCreating project message...")
            message = Message(
                topic="project.new",
                content=project_spec,
                sender="test_script"
            )

            print("\nSending project creation request...")
            response = await agent.process_message(message)
            
            # Use the updated print function
            await print_project_plan(response)

        finally:
            print("\nCleaning up agent...")
            await agent.cleanup()
            print("Agent cleanup complete")

            print("\nClosing Redis connection...")
            await cleanup_redis(redis_client)
            print("Redis connection closed")

    except Exception as e:
        print(f"\nError occurred: {str(e)}")
        import traceback
        traceback.print_exc()  # Print full traceback
        raise

if __name__ == "__main__":
    asyncio.run(main()) 