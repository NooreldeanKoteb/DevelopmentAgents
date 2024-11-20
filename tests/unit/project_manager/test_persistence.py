import pytest
import asyncio
from redis.asyncio import Redis
from datetime import datetime
from agents.project_manager.persistence import PersistenceManager
from core.schemas import TaskSchema, TaskStatus, TaskPriority, BusinessImpact

class TestPersistenceManager:
    @pytest.fixture(scope="function")
    async def redis_client(self):
        """Create a Redis client for testing."""
        client = Redis(host='localhost', port=6379, db=0)
        yield client
        
        # Proper cleanup
        try:
            await client.aclose()
            await client.connection_pool.disconnect()
        except Exception:
            pass  # Ignore cleanup errors

    @pytest.fixture(autouse=True)
    async def cleanup_redis(self):
        """Cleanup after each test."""
        yield
        redis = Redis(host='localhost', port=6379, db=0)
        try:
            await redis.flushdb()
            await redis.aclose()
            await redis.connection_pool.disconnect()
        except Exception:
            pass

    @pytest.fixture(autouse=True)
    async def setup_teardown(self, redis_client, event_loop):
        self.persistence = PersistenceManager(redis_client=redis_client)
        yield
        try:
            await self.persistence.cleanup()
        except Exception:
            pass

    @pytest.fixture
    def task_data(self):
        return {
            "id": "test-task",
            "name": "Test Task",
            "status": "pending",
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        }

    @pytest.mark.asyncio
    async def test_task_crud_operations(self, persistence):
        task = TaskSchema(
            id="test-task",
            name="Test Task",
            description="Test Description",
            status=TaskStatus.PENDING,
            priority=TaskPriority.MEDIUM,
            business_impact=BusinessImpact.LOW,
            estimated_duration="1.0",
            phase="phase-1"
        )
        
        # Test Create
        await persistence.save_task(task.id, task.model_dump())
        
        # Test Read
        saved_task = await persistence.get_task(task.id)
        assert saved_task.status == TaskStatus.PENDING
        
        # Test Update
        task.status = TaskStatus.IN_PROGRESS
        await persistence.save_task(task.id, task.model_dump())
        updated_task = await persistence.get_task(task.id)
        assert updated_task.status == TaskStatus.IN_PROGRESS

    @pytest.mark.asyncio
    async def test_task_indexing(self, persistence):
        task = TaskSchema(
            id="test-task",
            name="Test Task",
            status=TaskStatus.PENDING,
            priority=TaskPriority.MEDIUM,
            business_impact=BusinessImpact.LOW,
            estimated_duration="1.0",
            phase="phase-1"
        )
        
        # Save task
        await persistence.save_task(task.id, task.model_dump())
        
        # Test status indexing
        tasks = await persistence.get_tasks_by_status(TaskStatus.PENDING.value)
        assert len(tasks) == 1
        assert tasks[0].id == task.id
        assert tasks[0].status == TaskStatus.PENDING