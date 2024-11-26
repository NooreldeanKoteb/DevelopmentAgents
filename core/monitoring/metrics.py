from prometheus_client import Counter, Gauge, Histogram, REGISTRY
from typing import Dict, Optional, Any

class CoreMetrics:
    """Core system metrics."""
    _instance: Optional['CoreMetrics'] = None
    _metrics: Dict[str, Any] = {}
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            if not cls._metrics:
                cls._metrics = {
                    'message_count': Counter(
                        'core_messages_total',
                        'Total messages processed',
                        ['topic', 'status']
                    ),
                    'openai_tokens': Counter(
                        'core_openai_tokens_total',
                        'Total OpenAI tokens used',
                        ['model', 'operation']
                    ),
                    'openai_cost': Counter(
                        'core_openai_cost_total',
                        'Total OpenAI cost in dollars',
                        ['model']
                    ),
                    'agent_requests': Counter(
                        'agent_requests_total',
                        'Total requests by agent type and operation',
                        ['agent_type', 'operation']
                    ),
                    'agent_errors': Counter(
                        'agent_errors_total',
                        'Total errors by agent type and error type',
                        ['agent_type', 'error_type']
                    )
                }
        return cls._instance

    def __init__(self):
        # Access metrics through properties
        self.message_count = self._metrics.get('message_count')
        self.core_messages = self.message_count  # Alias for compatibility
        self.openai_tokens = self._metrics.get('openai_tokens')
        self.openai_cost = self._metrics.get('openai_cost')
        self.agent_requests = self._metrics.get('agent_requests')
        self.agent_errors = self._metrics.get('agent_errors')

    @classmethod
    def reset(cls):
        """Reset metrics and unregister from Prometheus."""
        if cls._metrics:
            for metric in cls._metrics.values():
                try:
                    if metric.describe()[0].name in REGISTRY._names_to_collectors:
                        REGISTRY.unregister(metric)
                except KeyError:
                    continue
        cls._metrics = {}
        cls._instance = None