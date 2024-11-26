from typing import Dict, Any, Optional, List, Callable, Awaitable
import asyncio
from datetime import datetime
from .message import Message
from .queue import MessageQueue
from core.config import monitor_operation
from collections import defaultdict
import logging

class MessageBroker:
    """Handles message routing and delivery between agents."""
    
    def __init__(self):
        self.queues: Dict[str, MessageQueue] = {}
        self.subscribers: Dict[str, List[Callable[[Message], Awaitable[None]]]] = defaultdict(list)
        self.error_handlers = []
        self._closed = False
        self._running = True
        self._tasks = set()
        
    async def initialize(self) -> None:
        """Initialize broker resources."""
        if self._closed:
            raise RuntimeError("Broker is closed")
        self._running = True
        self._tasks = set()
    
    async def close(self):
        """Close broker and cleanup resources."""
        self._running = False
        self.subscribers.clear()
        self.error_handlers.clear()
    
    @monitor_operation(agent_type="broker", operation="publish")
    async def publish(self, message: Message) -> None:
        """Publish a message to all subscribers of the topic."""
        if not self._running:
            return
            
        topic = message.topic
        
        if topic not in self.queues:
            self.queues[topic] = MessageQueue()
            
        await self.queues[topic].put(message)
        
        # Notify subscribers
        if topic in self.subscribers:
            tasks = [
                asyncio.create_task(self._safe_handle(subscriber, message))
                for subscriber in self.subscribers[topic]
            ]
            self._tasks.update(tasks)
            for task in tasks:
                task.add_done_callback(self._tasks.discard)
    
    async def _safe_handle(self, handler, message):
        """Safely execute handler with error handling."""
        try:
            await handler(message)
        except Exception as e:
            # Ensure error handlers are called
            await self._handle_error(e)
            
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
    
    def on_error(self, handler: Callable):
        """Register an error handler."""
        self.error_handlers.append(handler)
        
    async def _handle_error(self, error: Exception):
        """Handle error by notifying all error handlers."""
        for handler in self.error_handlers:
            try:
                await handler(error)
            except Exception as e:
                # Log secondary errors but don't propagate
                logging.error(f"Error in error handler: {e}")
    
    async def cleanup(self) -> None:
        """Cleanup broker resources."""
        self._running = False
        
        # Cancel all running tasks
        for task in self._tasks:
            task.cancel()
            
        # Wait for tasks to complete
        if self._tasks:
            await asyncio.gather(*self._tasks, return_exceptions=True)
            
        # Clear subscribers and tasks
        self.subscribers.clear()
        self._tasks.clear()
        self.error_handlers.clear()
    