import os
import sys
import pytest
from core.config.settings import Settings
from agents.director.agent import DirectorAgent
from agents.director.task_manager import TaskManager
from agents.director.resource_manager import ResourceManager
from agents.director.planner import ProjectPlanner
from agents.director.persistence import PersistenceManager
from core.schemas import (
    TaskSchema, TaskStatus, TaskPriority,
    BusinessImpact, ResourceSchema
)

# Add the project root directory to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

def pytest_configure(config):
    """Configure pytest-asyncio."""
    config.option.asyncio_mode = "auto"

@pytest.fixture
def test_settings():
    """Provide test settings."""
    return Settings(
        ENVIRONMENT="test",
        DEBUG=True,
        OPENAI_API_KEY="dummy-key-for-testing",
        LOG_LEVEL="INFO",
        VECTOR_DB_PATH="./data/vector_store",
        MAX_TOKENS=2000,
        RATE_LIMIT=50,
        REDIS_URL="redis://localhost:6379/0",
        PROMETHEUS_PORT=9090
    )