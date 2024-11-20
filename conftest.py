import os
import sys
import pytest
from core.config.settings import Settings
import redis.asyncio as aioredis
from agents.project_manager.agent import ProjectManagerAgent
from agents.project_manager.task_manager import TaskManager
from agents.project_manager.resource_manager import ResourceManager
from agents.project_manager.planner import ProjectPlanner
from agents.project_manager.persistence import PersistenceManager
from agents.project_manager.models import TaskData, ResourceData
from agents.project_manager.enums import TaskStatus, Priority, BusinessImpact
import asyncio
from redis.asyncio import Redis, ConnectionPool
from core.schemas import (
    TaskSchema, TaskStatus, TaskPriority,
    BusinessImpact, ResourceSchema
)

# Add the project root directory to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

def pytest_configure(config):
    """Configure pytest-asyncio."""
    config.option.asyncio_mode = "auto"

@pytest.fixture(scope="function")
def event_loop():
    """Create a new event loop for each test."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    yield loop
    try:
        loop.close()
    except:
        pass

@pytest.fixture(scope="function")
async def redis_pool():
    """Create a Redis connection pool."""
    pool = ConnectionPool(host='localhost', port=6379, db=0)
    yield pool
    try:
        await pool.disconnect()
    except:
        pass

@pytest.fixture(scope="function")
async def redis_client(redis_pool):
    """Create a Redis client for testing."""
    client = Redis(connection_pool=redis_pool)
    await client.flushdb()
    yield client
    try:
        await client.aclose()
    except:
        pass

@pytest.fixture(scope="function")
async def persistence_manager(redis_client):
    """Create a persistence manager for testing."""
    manager = PersistenceManager(redis_client=redis_client)
    yield manager
    try:
        await manager.cleanup()
    except:
        pass

@pytest.fixture
def test_settings():
    return Settings(
        ENVIRONMENT="development",
        DEBUG=True,
        OPENAI_API_KEY="dummy-key-for-testing",
        LOG_LEVEL="INFO",
        VECTOR_DB_PATH="./data/vector_store",
        MAX_TOKENS=2000,
        RATE_LIMIT=50,
        REDIS_URL="redis://localhost:6379/0",
        PROMETHEUS_PORT=9090
    ) 

@pytest.fixture
async def task_manager(persistence_manager):
    return TaskManager(persistence=persistence_manager)

@pytest.fixture(scope="function")
async def resource_manager(persistence_manager):
    """Create a resource manager for testing."""
    manager = ResourceManager(persistence=persistence_manager)
    yield manager

@pytest.fixture
async def planner():
    return ProjectPlanner()

@pytest.fixture
async def project_manager(task_manager, resource_manager, planner):
    return ProjectManagerAgent(
        task_manager=task_manager,
        resource_manager=resource_manager,
        planner=planner
    )

@pytest.fixture
def sample_message():
    return {
        "type": "task_creation",
        "content": {
            "name": "Test Task",
            "description": "Test Description",
            "priority": "HIGH",
            "business_impact": "MEDIUM",
            "estimated_duration": 2.0,
            "dependencies": []
        }
    }

@pytest.fixture
def sample_task_data():
    return TaskSchema(
        id="test-task",
        name="Test Task",
        description="Test Description",
        status=TaskStatus.PENDING,
        priority=TaskPriority.HIGH,
        business_impact=BusinessImpact.MEDIUM,
        estimated_duration="2.0",
        phase="testing",
        dependencies=[]
    )

@pytest.fixture
def sample_resource_data():
    return ResourceData(
        id="test-resource",
        name="Test Resource",
        type="agent",
        status="active",
        capabilities=["python", "testing"],
        current_load=0.0,
        capacity=1.0,
        performance_score=0.8
    ) 