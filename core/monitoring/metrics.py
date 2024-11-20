from prometheus_client import Counter, Histogram, Gauge
from typing import Dict, Any

class CoreMetrics:
    """Core system metrics collection."""
    
    def __init__(self):
        # Message metrics
        self.message_count = Counter(
            'core_messages_total',
            'Total messages processed',
            ['topic', 'status']
        )
        
        self.message_processing_time = Histogram(
            'core_message_processing_seconds',
            'Message processing duration',
            ['topic']
        )
        
        # Storage metrics
        self.vector_store_size = Gauge(
            'core_vector_store_size_bytes',
            'Vector store size in bytes'
        )
        
        self.message_store_size = Gauge(
            'core_message_store_size_bytes',
            'Message store size in bytes'
        )
        
        # OpenAI metrics
        self.openai_tokens = Counter(
            'core_openai_tokens_total',
            'Total OpenAI tokens used',
            ['model', 'operation']
        )
        
        self.openai_cost = Counter(
            'core_openai_cost_dollars',
            'Total OpenAI cost in dollars',
            ['model']
        ) 