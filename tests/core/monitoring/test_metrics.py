import pytest
from prometheus_client import REGISTRY
from core.monitoring.metrics import CoreMetrics

@pytest.fixture
def metrics():
    return CoreMetrics()

def test_message_metrics(metrics):
    """Test message-related metrics."""
    metrics.message_count.labels(topic="test", status="success").inc()
    
    value = REGISTRY.get_sample_value(
        'core_messages_total',
        {'topic': 'test', 'status': 'success'}
    )
    assert value == 1

def test_openai_metrics(metrics):
    """Test OpenAI metrics."""
    metrics.openai_tokens.labels(
        model="gpt-4",
        operation="completion"
    ).inc(100)
    
    metrics.openai_cost.labels(model="gpt-4").inc(0.02)
    
    tokens = REGISTRY.get_sample_value(
        'core_openai_tokens_total',
        {'model': 'gpt-4', 'operation': 'completion'}
    )
    cost = REGISTRY.get_sample_value(
        'core_openai_cost_dollars',
        {'model': 'gpt-4'}
    )
    
    assert tokens == 100
    assert cost == 0.02 