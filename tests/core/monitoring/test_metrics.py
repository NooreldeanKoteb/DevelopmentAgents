import pytest
from prometheus_client import REGISTRY
from core.monitoring.metrics import CoreMetrics

@pytest.fixture(autouse=True)
def clean_registry():
    """Clean the metrics registry before each test."""
    collectors = list(REGISTRY._collector_to_names.keys())
    for collector in collectors:
        REGISTRY.unregister(collector)
    CoreMetrics.reset()
    yield

@pytest.fixture
def metrics():
    """Create fresh metrics instance."""
    return CoreMetrics()

def test_message_metrics(metrics):
    """Test message-related metrics."""
    metrics.message_count.labels(type="test").inc()
    
    value = REGISTRY.get_sample_value(
        'core_messages_total',
        {'type': 'test'}
    )
    assert value == 1

def test_token_usage_tracking(metrics):
    """Test OpenAI token usage tracking."""
    metrics.track_token_usage("gpt-4", 100, 50)
    
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

def test_multiple_models(metrics):
    """Test tracking multiple models."""
    metrics.track_token_usage("gpt-4", 100, 50)
    metrics.track_token_usage("gpt-3.5-turbo", 200, 100)
    
    gpt4_tokens = REGISTRY.get_sample_value(
        'openai_tokens_total',
        {'model': 'gpt-4'}
    )
    gpt35_tokens = REGISTRY.get_sample_value(
        'openai_tokens_total',
        {'model': 'gpt-3.5-turbo'}
    )
    
    assert gpt4_tokens == 150
    assert gpt35_tokens == 300