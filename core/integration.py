"""Module to handle core integration checks and initialization."""
import asyncio
from typing import Optional, Dict, Any
from redis.asyncio import Redis
from prometheus_client import start_http_server
import logging
import socket
from contextlib import closing
from copy import deepcopy

from .config import get_settings
from .messaging import MessageBroker
from .openai import OpenAIClient
from .storage import VectorStore, MessageStore
from .monitoring import CoreMetrics, CoreLogger

class CoreIntegration:
    """Handles core service integration and health checks."""
    
    def __init__(self):
        self.settings = get_settings()
        
        # Message and Communication
        self.message_broker: Optional[MessageBroker] = None
        self.openai_client: Optional[OpenAIClient] = None
        
        # Storage
        self.redis: Optional[Redis] = None
        self.vector_store: Optional[VectorStore] = None
        self.message_store: Optional[MessageStore] = None
        
        # Monitoring
        self.metrics: Optional[CoreMetrics] = None
        self.logger: Optional[CoreLogger] = None
        
        # State
        self.initialized: bool = False
        self._health_check_interval: int = 60  # seconds
        self._health_check_task: Optional[asyncio.Task] = None
            
    def _get_free_port(self) -> int:
        """Get a free port number."""
        with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as s:
            s.bind(('', 0))
            s.listen(1)
            port = s.getsockname()[1]
            return port

    async def initialize(self) -> None:
        """Initialize all services."""
        if self.initialized:
            return
            
        try:
            # Create a copy of settings and update with dynamic ports
            self.settings = deepcopy(get_settings())
            self.settings.SERVER_PORT = self._get_free_port()
            self.settings.PROMETHEUS_PORT = self._get_free_port()
            
            # Initialize Redis with unique db
            db_index = self._get_free_port() % 16  # Use port number to get a unique DB index
            self.redis = Redis.from_url(
                f"{self.settings.REDIS_URL}/{db_index}",
                decode_responses=True
            )
            await self.redis.ping()
            
            # Initialize other services
            self.message_broker = MessageBroker()
            self.openai_client = OpenAIClient()
            self.vector_store = VectorStore()
            self.message_store = MessageStore(redis=self.redis)
            self.metrics = CoreMetrics()
            self.logger = CoreLogger()
            
            # Start health check loop
            self._health_check_task = asyncio.create_task(self._health_check_loop())
            
            self.initialized = True
            
        except Exception as e:
            await self.cleanup()
            raise RuntimeError(f"Core integration failed: {str(e)}")
            
    async def health_check(self) -> Dict[str, Any]:
        """Check health of all services."""
        health_status = {
            "status": "healthy",
            "services": {},  # Initialize services dict first
            "timestamp": asyncio.get_running_loop().time()
        }
        
        try:
            # Check Redis
            try:
                await self.redis.ping()
                health_status["services"]["redis"] = {"status": "healthy"}
            except Exception as e:
                if self.metrics:
                    self.metrics.error_count.inc()
                    self.metrics.error_types.labels("redis_error").inc()
                health_status["services"]["redis"] = {
                    "status": "unhealthy",
                    "error": str(e)
                }
                health_status["status"] = "unhealthy"
            
            # Check message broker
            if self.message_broker:
                queue_size = sum(len(q) for q in self.message_broker.queues.values())
                broker_status = "degraded" if queue_size > 1000 else "healthy"
                health_status["services"]["message_broker"] = {
                    "status": broker_status,
                    "queue_size": queue_size
                }
            
            # Check other services
            health_status["services"]["vector_store"] = {
                "status": "healthy" if self.vector_store else "unhealthy"
            }
            health_status["services"]["message_store"] = {
                "status": "healthy" if self.message_store else "unhealthy"
            }
            
            # Determine overall status
            service_statuses = [s["status"] for s in health_status["services"].values()]
            if "unhealthy" in service_statuses:
                health_status["status"] = "unhealthy"
            elif "degraded" in service_statuses:
                health_status["status"] = "degraded"
            
            return health_status
            
        except Exception as e:
            # Ensure we return a properly structured response even on unexpected errors
            return {
                "status": "unhealthy",
                "services": {
                    "redis": {
                        "status": "unhealthy",
                        "error": str(e)
                    }
                },
                "timestamp": asyncio.get_running_loop().time()
            }
            
    async def _health_check_loop(self) -> None:
        """Run periodic health checks."""
        while True:
            try:
                health_status = await self.health_check()
                if health_status["status"] != "healthy":
                    self.logger.logger.warning(
                        "Unhealthy service detected",
                        extra={"health_status": health_status}
                    )
            except Exception as e:
                self.logger.logger.error(
                    "Health check loop error",
                    extra={"error": str(e)}
                )
            await asyncio.sleep(self._health_check_interval)
            
    async def cleanup(self) -> None:
        """Cleanup all services."""
        if self._health_check_task:
            self._health_check_task.cancel()
            try:
                await self._health_check_task
            except asyncio.CancelledError:
                pass

        # Cleanup services in order
        if self.message_broker:
            await self.message_broker.close()
            
        if self.vector_store:
            await self.vector_store.cleanup()
            
        if self.redis:
            await self.redis.close()

        self.initialized = False
        await asyncio.sleep(0.1)
        
    async def __aenter__(self):
        """Async context manager entry."""
        await self.initialize()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.cleanup() 