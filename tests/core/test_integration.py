import pytest
import asyncio
from unittest.mock import AsyncMock, patch
from redis.asyncio import Redis
from prometheus_client import REGISTRY

from core.integration import CoreIntegration
from core.messaging import Message
from core.schemas import TaskSchema, TaskStatus
from core.openai import OpenAIError

@pytest.fixture
async def core():
    """Provide a CoreIntegration instance with mocked services."""
    with patch('redis.asyncio.Redis.ping', new_callable=AsyncMock) as mock_ping:
        mock_ping.return_value = True
        integration = CoreIntegration()
        await integration.initialize()
        yield integration
        await integration.cleanup()

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
    # Simulate large queue size
    test_message = Message(
        topic="test",
        content={"test": "data"},
        sender="test"
    )
    
    # Fill queue beyond threshold
    for _ in range(1001):
        await core.message_broker.publish(test_message)
    
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
    # Trigger some actions that should record metrics
    test_message = Message(
        topic="test",
        content={"test": "data"},
        sender="test"
    )
    await core.message_broker.publish(test_message)
    
    # Check metrics
    message_count = REGISTRY.get_sample_value(
        'core_messages_total',
        {'topic': 'test', 'status': 'success'}
    )
    assert message_count > 0

@pytest.mark.asyncio
async def test_logging_integration(core, caplog):
    """Test logging functionality."""
    # Trigger an error condition
    with patch('redis.asyncio.Redis.ping', 
              new_callable=AsyncMock) as mock_ping:
        mock_ping.side_effect = Exception("Test error")
        health_status = await core.health_check()
    
    # Check logs
    assert any("Test error" in record.message for record in caplog.records)

@pytest.mark.asyncio
async def test_cleanup(core):
    """Test cleanup procedure."""
    # Add some data to clean up
    test_message = Message(
        topic="test",
        content={"test": "data"},
        sender="test"
    )
    await core.message_broker.publish(test_message)
    
    # Perform cleanup
    await core.cleanup()
    
    assert not core.initialized
    assert core._health_check_task.cancelled()
    assert all(queue.empty() for queue in core.message_broker.queues.values())

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
    # Test message flow
    test_message = Message(
        topic="tasks",
        content=TaskSchema(
            id="test-task",
            name="Test Task"
        ).model_dump(),
        sender="test"
    )
    
    # Publish message
    await core.message_broker.publish(test_message)
    
    # Store in message store
    await core.message_store.store_message(test_message)
    
    # Retrieve from message store
    messages = await core.message_store.get_messages("tasks")
    assert len(messages) > 0
    assert messages[0].id == test_message.id 