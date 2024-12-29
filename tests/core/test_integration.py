import pytest
import asyncio
from unittest.mock import AsyncMock, patch
from redis.asyncio import Redis
from prometheus_client import REGISTRY
import logging
from unittest.mock import MagicMock

from core.integration import CoreIntegration
from core.messaging import Message
from core.openai import OpenAIError
from core.monitoring import CoreMetrics, CoreLogger
from core.storage import MessageStore
from core.schemas import TaskSchema
from agents.director.enums import TaskStatus, TaskPriority, BusinessImpact

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
async def core(clean_registry):
    """Provide a CoreIntegration instance."""
    integration = CoreIntegration()
    await integration.initialize()
    try:
        yield integration
    finally:
        await integration.cleanup()

@pytest.fixture(autouse=True)
def clean_registry():
    """Clean the metrics registry before each test."""
    collectors = list(REGISTRY._collector_to_names.keys())
    for collector in collectors:
        REGISTRY.unregister(collector)
    CoreMetrics.reset()
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
    core.metrics.message_count.labels(type="test").inc()
    
    # Verify metric was recorded
    value = REGISTRY.get_sample_value(
        'core_messages_total',
        {'type': 'test'}
    )
    assert value == 1

    # Test OpenAI metrics
    core.metrics.track_token_usage("gpt-4", 100, 50)
    
    tokens = REGISTRY.get_sample_value(
        'openai_tokens_total',
        {'model': 'gpt-4'}
    )
    assert tokens == 150
    
    cost = REGISTRY.get_sample_value(
        'openai_cost_total',
        {'model': 'gpt-4'}
    )
    assert cost > 0

@pytest.mark.asyncio
async def test_error_handling_integration(core):
    """Test error handling through metrics instead of logs."""
    # Mock metrics
    mock_metrics = MagicMock()
    mock_metrics.error_count = MagicMock()
    mock_metrics.error_types = MagicMock()
    mock_metrics.error_types.labels = MagicMock(return_value=MagicMock())
    core.metrics = mock_metrics
    
    # Simulate Redis failure
    core.redis.ping = AsyncMock(side_effect=Exception("Test error"))
    
    # Perform health check
    health_status = await core.health_check()
    
    # Verify through metrics and status
    assert health_status["status"] == "unhealthy"
    assert "Test error" in health_status["services"]["redis"]["error"]
    mock_metrics.error_count.inc.assert_called()

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
        
        core = CoreIntegration()
        try:
            await core.initialize()
        except RuntimeError as exc:
            assert "Connection failed" in str(exc)
        finally:
            if hasattr(core, 'cleanup'):
                await core.cleanup()

@pytest.mark.asyncio
async def test_service_integration(core):
    """Test integration between services."""
    message_id = "test-message-id"
    test_message = Message(
        id=message_id,
        topic="tasks",
        content=TaskSchema(
            id="test-task",
            name="Test Task",
            description="Test Description",
            priority=TaskPriority.MEDIUM,
            status=TaskStatus.PENDING,
            phase="phase-1"
        ).model_dump(),
        sender="test"
    )
    
    await core.redis.flushdb()
    await core.message_store.store_message(test_message)
    messages = await core.message_store.get_messages("tasks")
    
    assert len(messages) > 0, "No messages retrieved"
    retrieved_message = messages[0]
    assert retrieved_message.id == message_id