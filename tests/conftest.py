import pytest
import asyncio
import sys
from redis.asyncio import Redis, ConnectionPool
from typing import AsyncGenerator
from prometheus_client import REGISTRY, CollectorRegistry
from agents.project_manager.persistence import PersistenceManager
from agents.project_manager.task_manager import TaskManager
from agents.project_manager.resource_manager import ResourceManager
from agents.project_manager.planner import ProjectPlanner
from agents.project_manager.agent import ProjectManagerAgent
from core.config.settings import Settings
from core.integration import CoreIntegration
from core.storage.message_store import MessageStore
from core.monitoring import CoreMetrics

def pytest_configure(config):
    """Configure pytest-asyncio."""
    config.addinivalue_line(
        "markers",
        "asyncio: mark test as requiring asyncio"
    )
    config.option.asyncio_mode = "auto"

# Track all Redis connections
_redis_pools = set()
_redis_clients = set()

@pytest.fixture(scope="session")
def event_loop():
    """Create an event loop for the session."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    yield loop
    loop.close()

@pytest.fixture(autouse=True)
def clean_prometheus_registry():
    """Clear the Prometheus registry before each test."""
    collectors = list(REGISTRY._collector_to_names.keys())
    for collector in collectors:
        REGISTRY.unregister(collector)
    yield

@pytest.fixture(scope="function")
async def redis_pool():
    """Create a Redis connection pool."""
    pool = ConnectionPool(host='localhost', port=6379, db=0)
    _redis_pools.add(pool)
    try:
        yield pool
    finally:
        _redis_pools.discard(pool)
        await pool.disconnect()

@pytest.fixture(scope="function")
async def redis_client(redis_pool):
    """Create a Redis client for testing."""
    client = Redis(connection_pool=redis_pool, decode_responses=True)
    _redis_clients.add(client)
    try:
        await client.flushdb()
        yield client
    finally:
        _redis_clients.discard(client)
        await client.aclose()

@pytest.fixture(scope="function")
async def persistence_manager(redis_client):
    """Create a persistence manager for testing."""
    manager = PersistenceManager(redis_client=redis_client)
    try:
        yield manager
    finally:
        await manager.cleanup()

@pytest.fixture(scope="function")
async def task_manager(persistence_manager):
    """Create a task manager for testing."""
    manager = TaskManager(persistence=persistence_manager)
    yield manager

@pytest.fixture(scope="function")
async def planner():
    """Create a project planner for testing."""
    return ProjectPlanner()

@pytest.fixture(scope="function")
async def resource_manager(persistence_manager):
    """Create a resource manager for testing."""
    manager = ResourceManager(persistence_manager=persistence_manager)
    yield manager

@pytest.fixture(scope="function")
async def project_manager(task_manager, resource_manager, planner):
    """Create a project manager for testing."""
    manager = ProjectManagerAgent(
        task_manager=task_manager,
        resource_manager=resource_manager,
        planner=planner
    )
    yield manager

@pytest.fixture(scope="function")
async def core_integration():
    """Provide a CoreIntegration instance."""
    integration = CoreIntegration()
    await integration.initialize()
    try:
        yield integration
    finally:
        await integration.cleanup()

@pytest.fixture(autouse=True)
async def cleanup_redis():
    """Ensure all Redis connections are closed."""
    yield
    
    loop = asyncio.get_running_loop()
    
    # Close all Redis clients first
    for client in list(_redis_clients):
        try:
            await client.aclose()
        except Exception:
            pass
        _redis_clients.discard(client)
    
    # Then close all pools
    for pool in list(_redis_pools):
        try:
            await pool.disconnect()
        except Exception:
            pass
        _redis_pools.discard(pool)

    # Wait a bit for connections to fully close
    await asyncio.sleep(0.1)

@pytest.fixture(autouse=True)
async def cleanup_after_test():
    """Cleanup after each test."""
    yield
    
    try:
        loop = asyncio.get_running_loop()
        
        # First cleanup Redis
        await cleanup_redis.__wrapped__()
        
        # Then handle remaining tasks
        tasks = [t for t in asyncio.all_tasks(loop) 
                if t is not asyncio.current_task(loop)]
        
        for task in tasks:
            task.cancel()
        
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
            
    except Exception as e:
        print(f"Error during cleanup: {e}")

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

@pytest.fixture(autouse=True)
async def clean_redis():
    """Clean Redis before and after each test."""
    redis = Redis.from_url("redis://localhost:6379/0", decode_responses=True)
    try:
        await redis.flushdb()
        yield
    finally:
        await redis.aclose()

@pytest.fixture(autouse=True)
def clean_metrics():
    """Clean Prometheus metrics before each test."""
    CoreMetrics.reset()
    for collector in list(REGISTRY._collector_to_names.keys()):
        REGISTRY.unregister(collector)

@pytest.fixture(scope="function")
async def message_store(redis_client):
    """Create a message store for testing."""
    return MessageStore(redis=redis_client)

@pytest.fixture(autouse=True)
def clean_registry():
    """Clean up the Prometheus registry between tests."""
    collectors = list(REGISTRY._collector_to_names.keys())
    for collector in collectors:
        REGISTRY.unregister(collector)
    yield