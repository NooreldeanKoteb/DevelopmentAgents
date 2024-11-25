import pytest
import asyncio
from unittest.mock import AsyncMock, patch
from redis.asyncio import Redis
from prometheus_client import REGISTRY
import logging

from core.integration import CoreIntegration
from core.messaging import Message
from core.schemas import TaskSchema, TaskStatus
from core.openai import OpenAIError
from core.monitoring import CoreMetrics, CoreLogger
from core.storage import MessageStore

@pytest.fixture(autouse=True)
async def cleanup_servers():
    """Ensure servers are cleaned up after each test."""
    yield
    # Allow time for servers to shut down
    await asyncio.sleep(0.1)

@pytest.fixture(autouse=True)
async def cleanup_ports():
    """Ensure ports are cleaned up after each test."""
    yield
    # Allow time for ports to be released
    await asyncio.sleep(0.1)

@pytest.fixture
async def core():
    """Provide a CoreIntegration instance with mocked services."""
    with patch('redis.asyncio.Redis.ping', new_callable=AsyncMock) as mock_ping, \
         patch('core.monitoring.CoreMetrics') as mock_metrics, \
         patch('core.monitoring.CoreLogger') as mock_logger, \
         patch('prometheus_client.start_http_server') as mock_prometheus:  # Mock Prometheus server
            
        mock_ping.return_value = True
        integration = CoreIntegration()
        await integration.initialize()
        yield integration
        await integration.cleanup()

@pytest.fixture(autouse=True)
def clean_registry():
    """Clean up the Prometheus registry between tests."""
    collectors = list(REGISTRY._collector_to_names.keys())
    for collector in collectors:
        REGISTRY.unregister(collector)
    yield

@pytest.mark.asyncio
async def test_initialization(core):
    """Test successful initialization of all services."""
    assert core.initialized
    assert core.redis is not None
    assert core.message_broker is not None
    assert core.openai_client is not None
    assert core.vector_store is not None
    assert core.message_store is not None
    assert core.metrics is not None
    assert core.logger is not None
    assert core._health_check_task is not None

@pytest.mark.asyncio
async def test_health_check(core):
    """Test health check functionality."""
    health_status = await core.health_check()
    
    assert health_status["status"] == "healthy"
    assert "services" in health_status
    assert "redis" in health_status["services"]
    assert "message_broker" in health_status["services"]
    assert "vector_store" in health_status["services"]
    assert "message_store" in health_status["services"]
    assert "timestamp" in health_status

@pytest.mark.asyncio
async def test_degraded_health_status(core):
    """Test health status when services are degraded."""
    # Mock the message broker queues to simulate large queue size
    core.message_broker.queues = {
        "test": [Message(
            topic="test",
            content={"test": "data"},
            sender="test"
        ) for _ in range(1001)]  # Create list with 1001 messages
    }
    
    health_status = await core.health_check()
    assert health_status["status"] == "degraded"
    assert health_status["services"]["message_broker"]["status"] == "degraded"

@pytest.mark.asyncio
async def test_unhealthy_status(core):
    """Test health status when services fail."""
    # Simulate Redis failure
    core.redis.ping = AsyncMock(side_effect=Exception("Redis connection failed"))
    
    health_status = await core.health_check()
    assert health_status["status"] == "unhealthy"
    assert health_status["services"]["redis"]["status"] == "unhealthy"

@pytest.mark.asyncio
async def test_metrics_integration(core):
    """Test metrics recording."""
    # Initialize metrics directly
    core.metrics = CoreMetrics()
    
    # Record a message metric
    core.metrics.message_count.labels(
        topic="test",
        status="success"
    ).inc()
    
    # Check metrics
    message_count = REGISTRY.get_sample_value(
        'core_messages_total',
        {'topic': 'test', 'status': 'success'}
    )
    assert message_count is not None
    assert message_count > 0

@pytest.mark.asyncio
async def test_logging_integration(core, caplog):
    """Test logging functionality."""
    # Create and configure a real logger
    logger = CoreLogger()
    logger.logger.propagate = True
    logger.logger.handlers = []  # Clear existing handlers
    logger.logger.addHandler(logging.StreamHandler())
    logger.logger.setLevel(logging.ERROR)
    
    # Replace the mock logger with our real one
    core.logger = logger
    
    # Simulate Redis failure
    core.redis.ping.side_effect = Exception("Test error")
    
    # Perform health check
    await core.health_check()
    
    # Verify logs
    assert any(
        "Test error" in record.message 
        for record in caplog.records
    ), f"Expected error log not found. Available logs: {caplog.records}"

@pytest.mark.asyncio
async def test_cleanup(core):
    """Test cleanup functionality."""
    # Verify initial state
    assert core.initialized
    assert core.message_broker is not None
    
    # Perform cleanup
    await core.cleanup()
    
    # Verify cleanup results
    assert not core.initialized
    assert not core.message_broker._running
    assert len(core.message_broker.subscribers) == 0
    assert len(core.message_broker._tasks) == 0

@pytest.mark.asyncio
async def test_context_manager():
    """Test async context manager functionality."""
    async with CoreIntegration() as core:
        assert core.initialized
        health_status = await core.health_check()
        assert health_status["status"] == "healthy"
    
    assert not core.initialized

@pytest.mark.asyncio
async def test_health_check_loop():
    """Test the health check loop."""
    with patch('core.integration.CoreIntegration.health_check', 
              new_callable=AsyncMock) as mock_health_check:
        mock_health_check.return_value = {"status": "healthy"}
        
        core = CoreIntegration()
        await core.initialize()
        
        # Let the health check loop run for a bit
        await asyncio.sleep(2)
        
        assert mock_health_check.called
        await core.cleanup()

@pytest.mark.asyncio
async def test_error_handling():
    """Test error handling during initialization."""
    with patch('redis.asyncio.Redis.ping', 
              new_callable=AsyncMock) as mock_ping:
        mock_ping.side_effect = Exception("Connection failed")
        
        with pytest.raises(RuntimeError) as exc_info:
            core = CoreIntegration()
            await core.initialize()
        
        assert "Connection failed" in str(exc_info.value)

@pytest.mark.asyncio
async def test_service_integration(core):
    """Test integration between services."""
    # Create test message with fixed ID
    message_id = "test-message-id"
    test_message = Message(
        id=message_id,
        topic="tasks",
        content=TaskSchema(
            id="test-task",
            name="Test Task"
        ).model_dump(),
        sender="test"
    )
    
    # Use the existing message store from core
    await core.redis.flushdb()  # Clear existing messages
    
    # Store and retrieve message
    await core.message_store.store_message(test_message)
    messages = await core.message_store.get_messages("tasks")
    
    # Verify message
    assert len(messages) > 0, "No messages retrieved"
    retrieved_message = messages[0]
    assert retrieved_message.id == message_id, \
        f"Expected ID {message_id}, got {retrieved_message.id}"