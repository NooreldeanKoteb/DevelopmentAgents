from prometheus_client import Counter, REGISTRY
from typing import Dict, Optional

class CoreMetrics:
    """Core system metrics."""
    _instance: Optional['CoreMetrics'] = None
    _metrics: Dict[str, Counter] = {}
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            # Initialize metrics only once
            if not cls._metrics:
                cls._metrics = {
                    'core_messages': Counter(
                        'core_messages_total',
                        'Total messages processed',
                        ['topic', 'status']
                    ),
                    'message_count': Counter(
                        'core_message_count_total',
                        'Total message count by type',
                        ['topic', 'status']
                    ),
                    'openai_tokens': Counter(
                        'core_openai_tokens_total',
                        'Total OpenAI tokens used',
                        ['model', 'operation']
                    ),
                    'openai_cost': Counter(
                        'core_openai_cost_dollars',
                        'Total OpenAI cost in dollars',
                        ['model']
                    )
                }
        return cls._instance
    
    def __init__(self):
        # Access metrics through properties
        self.core_messages = self._metrics.get('core_messages')
        self.message_count = self._metrics.get('message_count')
        self.openai_tokens = self._metrics.get('openai_tokens')
        self.openai_cost = self._metrics.get('openai_cost')
    
    @classmethod
    def reset(cls):
        """Reset the singleton instance and unregister metrics."""
        if cls._metrics:
            for name, metric in cls._metrics.items():
                try:
                    if metric.describe()[0].name in REGISTRY._names_to_collectors:
                        REGISTRY.unregister(metric)
                except KeyError:
                    continue
        cls._metrics = {}
        cls._instance = None