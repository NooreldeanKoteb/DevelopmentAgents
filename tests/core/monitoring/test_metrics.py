import pytest
from prometheus_client import REGISTRY, CollectorRegistry
from core.monitoring.metrics import CoreMetrics

@pytest.fixture(autouse=True)
def clean_registry():
    """Clean the metrics registry before each test."""
    for collector in list(REGISTRY._collector_to_names.keys()):
        REGISTRY.unregister(collector)
    yield

@pytest.fixture
def metrics():
    """Create fresh metrics instance."""
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
    # Increment metrics
    metrics.openai_tokens.labels(
        model="gpt-4",
        operation="completion"
    ).inc(100)
    
    metrics.openai_cost.labels(model="gpt-4").inc(0.02)
    
    # Get values using exact metric names
    tokens = REGISTRY.get_sample_value(
        'core_openai_tokens_total',  # Make sure this matches the name in CoreMetrics
        {'model': 'gpt-4', 'operation': 'completion'}
    )
    cost = REGISTRY.get_sample_value(
        'core_openai_cost_total',  # Updated to match CoreMetrics
        {'model': 'gpt-4'}
    )
    
    assert tokens == 100
    assert cost == 0.02 