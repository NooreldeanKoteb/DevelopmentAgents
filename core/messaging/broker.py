from typing import Dict, Any, Optional, List, Callable, Awaitable
import asyncio
from datetime import datetime
from .message import Message
from .queue import MessageQueue
from core.config import monitor_operation

class MessageBroker:
    """Handles message routing and delivery between agents."""
    
    def __init__(self):
        self.queues: Dict[str, MessageQueue] = {}
        self.subscribers: Dict[str, List[Callable[[Message], Awaitable[None]]]] = {}
        self.error_handlers = set()
        self._closed = False
        
    async def close(self):
        """Cleanup broker resources."""
        self._closed = True
        # Clear all subscriptions
        self.subscribers.clear()
        self.error_handlers.clear()
    
    @monitor_operation(agent_type="broker", operation="publish")
    async def publish(self, message: Message) -> None:
        """Publish a message to all subscribers of the topic."""
        if self._closed:
            raise RuntimeError("Broker is closed")
            
        topic = message.topic
        
        if topic not in self.queues:
            self.queues[topic] = MessageQueue()
            
        await self.queues[topic].put(message)
        
        # Notify subscribers
        if topic in self.subscribers:
            tasks = [
                subscriber(message) 
                for subscriber in self.subscribers[topic]
            ]
            await asyncio.gather(*tasks, return_exceptions=True)
    
    @monitor_operation(agent_type="broker", operation="subscribe")
    async def subscribe(
        self, 
        topic: str, 
        callback: Callable[[Message], Awaitable[None]]
    ) -> None:
        """Subscribe to a topic with a callback function."""
        if topic not in self.subscribers:
            self.subscribers[topic] = []
        self.subscribers[topic].append(callback)
        
        if topic not in self.queues:
            self.queues[topic] = MessageQueue()
    
    @monitor_operation(agent_type="broker", operation="unsubscribe")
    async def unsubscribe(
        self, 
        topic: str, 
        callback: Callable[[Message], Awaitable[None]]
    ) -> None:
        """Unsubscribe from a topic."""
        if topic in self.subscribers:
            self.subscribers[topic].remove(callback)
            
    async def get_message(self, topic: str) -> Optional[Message]:
        """Get the next message from a topic queue."""
        if topic not in self.queues:
            return None
        return await self.queues[topic].get()
    
    async def _handle_error(self, error: Exception):
        """Handle an error."""
        for handler in self.error_handlers:
            try:
                await handler(error)
            except Exception as e:
                await self._handle_error(e)
    