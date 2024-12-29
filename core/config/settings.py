from pydantic_settings import BaseSettings
from typing import Optional, Dict, Any, ClassVar
from enum import Enum
from pydantic import BaseModel, ConfigDict
import os

class Environment(str, Enum):
    """Application environment."""
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"

class Settings(BaseSettings):
    """Application settings with environment variable support."""
    model_config = ConfigDict(
        env_file = ".env",
        env_file_encoding = 'utf-8',
        case_sensitive = True
    )
    # Environment
    ENVIRONMENT: Environment = Environment.DEVELOPMENT
    DEBUG: bool = False
    
    # Agent Settings
    HEARTBEAT_TIMEOUT = 180  # Seconds before considering an agent offline

    # OpenAI
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "dummy-key-for-testing")
    if not OPENAI_API_KEY:
        raise ValueError("OPENAI_API_KEY environment variable is not set")
    OPENAI_MODEL: str = "gpt-4-turbo-preview"
    TEMPERATURE: float = 0.7
    MAX_TOKENS: int = 20000
    RATE_LIMIT: int = 50  # Requests per minute
    
    # Storage
    REDIS_URL: str = "redis://localhost:6379/0"
    VECTOR_DB_PATH: str = "./data/vector_store"
    
    # Monitoring
    LOG_LEVEL: str = "INFO"
    PROMETHEUS_PORT: int = 9090
    SERVER_PORT: int = 8000

    # OpenAI Configuration
    OPENAI_CONFIG: ClassVar[Dict[str, Any]] = {
        "api_key": OPENAI_API_KEY,
        "default_model": "gpt-4-turbo-preview",
        "max_retries": 3,
        "timeout": 30,
        "rate_limits": {
            "requests_per_minute": 60,
            "tokens_per_minute": 90000
        }
    }

    def validate_integration(self) -> bool:
        """Validate core integration settings."""
        try:
            # Check required settings
            assert self.OPENAI_API_KEY, "OpenAI API key is required"
            assert self.REDIS_URL, "Redis URL is required"
            
            # Validate rate limits
            assert self.RATE_LIMIT > 0, "Rate limit must be positive"
            assert self.MAX_TOKENS > 0, "Max tokens must be positive"
            
            # Validate ports
            assert 0 < self.PROMETHEUS_PORT < 65536, "Invalid Prometheus port"
            
            return True
            
        except AssertionError:
            return False

_settings = None

def get_settings() -> Settings:
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings 