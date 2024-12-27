from typing import Optional, Dict, Any
from prometheus_client import Counter, REGISTRY

class CoreMetrics:
    """Core metrics tracking for the entire system."""
    _instance: Optional['CoreMetrics'] = None
    _metrics: Dict[str, Any] = {}
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialize_metrics()
        return cls._instance

    def _initialize_metrics(self):
        """Initialize metrics only if they don't exist."""
        if not self._metrics:
            # Message metrics
            self._metrics['message_count'] = Counter(
                'core_messages_total',
                'Total messages processed',
                ['type']
            )
            
            # OpenAI metrics
            self._metrics['token_counter'] = Counter(
                'openai_tokens_total',
                'Total tokens used by model type',
                ['model']
            )
            self._metrics['cost_counter'] = Counter(
                'openai_cost_total',
                'Total cost in USD by model type',
                ['model']
            )
            
            # Set up property access
            self.message_count = self._metrics['message_count']
            self.token_counter = self._metrics['token_counter']
            self.cost_counter = self._metrics['cost_counter']
            
            # Model rate configuration
            self.model_rates = {
                "gpt-4": 0.03,
                "gpt-4-turbo": 0.01,
                "gpt-3.5-turbo": 0.002
            }

    def track_token_usage(self, model: str, prompt_tokens: int, completion_tokens: int) -> None:
        """Track OpenAI token usage and cost."""
        total_tokens = prompt_tokens + completion_tokens
        self.token_counter.labels(model=model).inc(total_tokens)
        
        # Calculate cost
        base_rate = self.model_rates.get(model.split(':')[0], 0.01)
        input_cost = (prompt_tokens / 1000) * base_rate
        output_cost = (completion_tokens / 1000) * (base_rate * 2)
        total_cost = input_cost + output_cost
        
        self.cost_counter.labels(model=model).inc(total_cost)

    @classmethod
    def reset(cls):
        """Reset all metrics for testing."""
        if cls._instance:
            for metric in cls._instance._metrics.values():
                try:
                    REGISTRY.unregister(metric)
                except KeyError:
                    continue
            cls._metrics = {}
            cls._instance = None
