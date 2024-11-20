import pytest
from prometheus_client import REGISTRY
from core.config.monitoring import monitor_operation

@pytest.mark.asyncio
async def test_monitor_operation_success():
    """Test monitoring decorator with successful operation."""
    
    @monitor_operation(agent_type="test", operation="success")
    async def test_operation():
        return "success"
    
    # Get initial metric values
    initial_requests = REGISTRY.get_sample_value(
        'agent_requests_total',
        {'agent_type': 'test', 'operation': 'success'}
    ) or 0
    
    result = await test_operation()
    
    # Verify operation succeeded
    assert result == "success"
    
    # Verify metrics were updated
    final_requests = REGISTRY.get_sample_value(
        'agent_requests_total',
        {'agent_type': 'test', 'operation': 'success'}
    )
    assert final_requests == initial_requests + 1

@pytest.mark.asyncio
async def test_monitor_operation_error():
    """Test monitoring decorator with failed operation."""
    
    @monitor_operation(agent_type="test", operation="error")
    async def test_operation():
        raise ValueError("Test error")
    
    # Get initial metric values
    initial_errors = REGISTRY.get_sample_value(
        'agent_errors_total',
        {'agent_type': 'test', 'error_type': 'ValueError'}
    ) or 0
    
    # Execute operation and verify it fails
    with pytest.raises(ValueError):
        await test_operation()
    
    # Verify error metrics were updated
    final_errors = REGISTRY.get_sample_value(
        'agent_errors_total',
        {'agent_type': 'test', 'error_type': 'ValueError'}
    )
    assert final_errors == initial_errors + 1

@pytest.mark.asyncio
async def test_monitor_operation_latency():
    """Test monitoring decorator records latency."""
    
    @monitor_operation(agent_type="test", operation="latency")
    async def test_operation():
        return "success"
    
    # Get initial histogram count
    initial_count = REGISTRY.get_sample_value(
        'agent_operation_duration_seconds_count',
        {'agent_type': 'test', 'operation': 'latency'}
    ) or 0
    
    await test_operation()
    
    # Verify histogram was updated
    final_count = REGISTRY.get_sample_value(
        'agent_operation_duration_seconds_count',
        {'agent_type': 'test', 'operation': 'latency'}
    )
    assert final_count == initial_count + 1 