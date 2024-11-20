import pytest
from prometheus_client import REGISTRY
from core.openai.usage import TokenUsageTracker

def test_token_usage_tracking():
    """Test token usage tracking."""
    tracker = TokenUsageTracker()
    
    # Track usage
    tracker.track_usage(
        model="gpt-4",
        prompt_tokens=100,
        completion_tokens=50
    )
    
    # Check metrics
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

def test_multiple_models():
    """Test tracking multiple models."""
    tracker = TokenUsageTracker()
    
    # Track different models
    tracker.track_usage("gpt-4", 100, 50)
    tracker.track_usage("gpt-3.5-turbo", 200, 100)
    
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