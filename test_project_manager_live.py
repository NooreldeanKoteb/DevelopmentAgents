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

async def main():
    try:
        # Clear metrics before anything else
        print("\nInitializing metrics...")
        clear_metrics()
        CoreMetrics.reset()
        print("Metrics initialized")
        
        # Setup Redis
        redis_client = await setup_redis()
        
        try:
            print("\nInitializing services...")
            # Initialize components
            persistence = PersistenceManager(redis_client=redis_client)
            task_service = TaskManager(persistence=persistence)
            resource_service = ResourceManager()
            print("Services initialized")

            print("\nCreating Project Manager agent...")
            # Create Project Manager agent without planner first
            agent = ProjectManagerAgent(
                name="Test Project Manager",
                agent_type="project_manager",
                task_service=task_service,
                resource_service=resource_service,
                planner_service=None,  # Set to None initially
                redis_client=redis_client
            )

            print("Initializing agent...")
            await agent.initialize()  # This will create the planner with agent reference
            print("Agent initialized successfully")

            try:
                # Project specification
                project_spec = {
                    "id": "test-project-1",
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
                    - Share your travel experiences
                    - Follow other users
                    - Like and comment on posts
                    - Search for places
                    - Create a community for travel enthusiasts

                    MAKE SURE ALL FIELDS ARE FILLED
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
                    "priority": TaskPriority.HIGH,
                    "business_impact": BusinessImpact.HIGH,
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
                print(f"Response: {response}")

                print("\nProject Plan Created:")
                print("====================")
                print(f"Project: {project_spec['name']}")
                print(f"Description: {project_spec['description'].strip()}")
                
                if response and response.content:
                    print("\nGenerated Tasks:")
                    print("===============")
                    for task in response.content.get("tasks", []):
                        print(f"\nTask: {task.name}")
                        print(f"Description: {task.description}")
                        print(f"Priority: {task.priority}")
                        print(f"Phase: {task.phase}")
                        print(f"Dependencies: {task.dependencies}")
                        print(f"Estimated Duration: {task.estimated_duration} days")

                    print("\nResource Allocation:")
                    print("===================")
                    for resource in response.content.get("resources", []):
                        print(f"\nResource: {resource.name}")
                        print(f"Type: {resource.type}")
                        print(f"Status: {resource.status}")
                else:
                    print("\nError: No response received from agent")

            finally:
                print("\nCleaning up agent...")
                await agent.cleanup()
                print("Agent cleanup complete")

            print("\nClosing Redis connection...")
            await cleanup_redis(redis_client)
            print("Redis connection closed")

        finally:
            print("\nClosing Redis connection...")
            await redis_client.close()
            print("Redis connection closed")

    except Exception as e:
        print(f"\nError occurred: {str(e)}")
        raise

if __name__ == "__main__":
    asyncio.run(main()) 