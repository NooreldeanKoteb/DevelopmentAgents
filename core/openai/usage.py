from datetime import datetime
from prometheus_client import Counter, Gauge

class TokenUsageTracker:
    """Tracks token usage and costs."""
    
    def __init__(self):
        self.token_counter = Counter(
            'openai_tokens_total',
            'Total tokens used by model type',
            ['model']
        )
        
        self.cost_gauge = Gauge(
            'openai_cost_total',
            'Total cost in USD by model type',
            ['model']
        )
        
        self.model_rates = {
            "gpt-4": 0.03,      # $0.03 per 1K tokens
            "gpt-4-turbo": 0.01,  # $0.01 per 1K tokens
            "gpt-3.5-turbo": 0.002  # $0.002 per 1K tokens
        }
        
    def track_usage(self, model: str, prompt_tokens: int, completion_tokens: int) -> None:
        """Track token usage and update metrics."""
        total_tokens = prompt_tokens + completion_tokens
        self.token_counter.labels(model=model).inc(total_tokens)
        
        # Calculate cost
        base_rate = self.model_rates.get(model.split(':')[0], 0.01)
        input_cost = (prompt_tokens / 1000) * base_rate
        output_cost = (completion_tokens / 1000) * (base_rate * 2)
        total_cost = input_cost + output_cost
        
        self.cost_gauge.labels(model=model).inc(total_cost) 