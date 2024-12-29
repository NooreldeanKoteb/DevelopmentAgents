from .config import Settings, get_settings
from .messaging import Message, MessageBroker
from .openai import OpenAIClient
from .schemas import (ResourceSchema, ResourceType)
from .monitoring.metrics import CoreMetrics

__all__ = [
    # Config
    'Settings',
    'get_settings',
    
    # Messaging
    'Message',
    'MessageBroker',
    
    # OpenAI
    'OpenAIClient',
    
    # Schemas
    'ResourceSchema'
    'ResourceType'

    # Monitoring
    'CoreMetrics'
] 

class Core:
    def __init__(self):
        self.metrics = CoreMetrics()
        self.openai_client = OpenAIClient(metrics=self.metrics) 