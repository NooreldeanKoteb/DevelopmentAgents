import pytest
import asyncio
from redis.asyncio import Redis, ConnectionPool
from agents.project_manager.persistence import PersistenceManager
from agents.project_manager.task_manager import TaskManager
from agents.project_manager.resource_manager import ResourceManager
from agents.project_manager.planner import ProjectPlanner
from agents.project_manager.agent import ProjectManagerAgent
from core.config.settings import Settings
from prometheus_client import REGISTRY

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for each test case."""
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="session")
async def redis_pool():
    """Create a Redis connection pool."""
    pool = ConnectionPool(host='localhost', port=6379, db=0)
    yield pool
    await pool.disconnect()

@pytest.fixture(scope="function")
async def redis_client(redis_pool):
    """Create a Redis client for testing."""
    client = Redis(connection_pool=redis_pool)
    yield client
    try:
        await client.close(close_connection_pool=False)
    except Exception:
        pass

@pytest.fixture(autouse=True)
async def cleanup_redis(redis_client):
    """Cleanup after each test."""
    yield
    await redis_client.flushdb()

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
async def persistence(redis_client):
    manager = PersistenceManager(redis_client=redis_client)
    yield manager

@pytest.fixture
async def task_manager(persistence):
    return TaskManager(persistence=persistence)

@pytest.fixture
async def resource_manager(persistence):
    return ResourceManager(persistence=persistence)

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

@pytest.fixture(autouse=True)
async def clean_redis():
    """Clean Redis before and after each test."""
    redis = Redis.from_url("redis://localhost:6379/0", decode_responses=True)
    await redis.flushdb()
    yield
    await redis.flushdb()
    await redis.close()

@pytest.fixture(autouse=True)
def clean_metrics():
    """Clean Prometheus metrics before each test."""
    for collector in list(REGISTRY._collector_to_names.keys()):
        REGISTRY.unregister(collector) 