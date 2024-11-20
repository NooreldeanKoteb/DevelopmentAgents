"""Module to handle core integration checks and initialization."""
import asyncio
from typing import Optional, Dict, Any
from redis.asyncio import Redis
from prometheus_client import start_http_server
import logging

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
        
    async def initialize(self) -> None:
        """Initialize all core services."""
        try:
            # Initialize monitoring first for logging
            self.metrics = CoreMetrics()
            self.logger = CoreLogger()
            self.logger.logger.info("Starting core services initialization")
            
            # Initialize Redis
            self.redis = Redis.from_url(
                self.settings.REDIS_URL,
                decode_responses=True
            )
            await self.redis.ping()
            self.logger.logger.info("Redis connection established")
            
            # Initialize storage services
            self.vector_store = VectorStore()
            self.message_store = MessageStore()
            self.logger.logger.info("Storage services initialized")
            
            # Initialize messaging
            self.message_broker = MessageBroker()
            self.logger.logger.info("Message broker initialized")
            
            # Initialize OpenAI client
            self.openai_client = OpenAIClient()
            self.logger.logger.info("OpenAI client initialized")
            
            # Start Prometheus metrics server
            start_http_server(self.settings.PROMETHEUS_PORT)
            self.logger.logger.info(
                f"Metrics server started on port {self.settings.PROMETHEUS_PORT}"
            )
            
            # Start health check loop
            self._health_check_task = asyncio.create_task(self._health_check_loop())
            
            self.initialized = True
            self.logger.logger.info("Core services initialization completed")
            
        except Exception as e:
            self.logger.logger.error(
                "Core integration failed",
                extra={"error": str(e), "error_type": type(e).__name__}
            )
            await self.cleanup()
            raise RuntimeError(f"Core integration failed: {str(e)}")
            
    async def health_check(self) -> Dict[str, Any]:
        """Check health of all core services."""
        health_status = {
            "status": "healthy",
            "services": {},
            "timestamp": asyncio.get_running_loop().time()
        }
        
        try:
            # Check Redis
            redis_status = {"status": "healthy"}
            try:
                if self.redis:
                    await self.redis.ping()
            except Exception as e:
                redis_status = {
                    "status": "unhealthy",
                    "error": str(e)
                }
            health_status["services"]["redis"] = redis_status
            
            # Check MessageBroker
            broker_status = {"status": "healthy"}
            try:
                if self.message_broker:
                    queue_sizes = {
                        name: queue.qsize() 
                        for name, queue in self.message_broker.queues.items()
                    }
                    broker_status["queue_sizes"] = queue_sizes
                    if any(size > 1000 for size in queue_sizes.values()):
                        broker_status["status"] = "degraded"
            except Exception as e:
                broker_status = {
                    "status": "unhealthy",
                    "error": str(e)
                }
            health_status["services"]["message_broker"] = broker_status
            
            # Check VectorStore
            vector_status = {"status": "healthy"}
            try:
                if self.vector_store:
                    test_embedding = [0.0] * 384
                    await self.vector_store.search(
                        "health_check",
                        test_embedding,
                        n_results=1
                    )
            except Exception as e:
                vector_status = {
                    "status": "unhealthy",
                    "error": str(e)
                }
            health_status["services"]["vector_store"] = vector_status
            
            # Check MessageStore
            message_store_status = {"status": "healthy"}
            try:
                if self.message_store:
                    await self.message_store.redis.ping()
            except Exception as e:
                message_store_status = {
                    "status": "unhealthy",
                    "error": str(e)
                }
            health_status["services"]["message_store"] = message_store_status
            
            # Update overall status
            service_statuses = [
                s["status"] for s in health_status["services"].values()
            ]
            if any(s == "unhealthy" for s in service_statuses):
                health_status["status"] = "unhealthy"
            elif any(s == "degraded" for s in service_statuses):
                health_status["status"] = "degraded"
                
            # Update metrics
            if self.metrics:
                self.metrics.message_count.labels(
                    topic="health_check",
                    status=health_status["status"]
                ).inc()
                
            return health_status
            
        except Exception as e:
            self.logger.logger.error(
                "Health check failed",
                extra={"error": str(e)}
            )
            return {
                "status": "unhealthy",
                "error": str(e),
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
        """Cleanup core services."""
        self.logger.logger.info("Starting core services cleanup")
        
        # Cancel health check loop
        if self._health_check_task:
            self._health_check_task.cancel()
            try:
                await self._health_check_task
            except asyncio.CancelledError:
                pass
        
        # Cleanup Redis connections
        if self.redis:
            await self.redis.close()
        if self.message_store:
            await self.message_store.redis.close()
            
        # Cleanup message broker
        if self.message_broker:
            for queue in self.message_broker.queues.values():
                while not queue.empty():
                    await queue.get()
                    
        self.initialized = False
        self.logger.logger.info("Core services cleanup completed")
        
    async def __aenter__(self):
        """Async context manager entry."""
        await self.initialize()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.cleanup() 