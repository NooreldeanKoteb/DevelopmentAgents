from pathlib import Path
from typing import Optional, Dict, Any
from pydantic_settings import BaseSettings
from functools import lru_cache
import logging

class Settings(BaseSettings):
    """Base configuration settings for the AI Development System."""
    
    # Project paths
    PROJECT_ROOT: Path = Path(__file__).parent.parent.parent
    
    # Environment
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    
    # OpenAI
    OPENAI_API_KEY: str
    OPENAI_MODEL: str = "gpt-4-turbo-preview"
    MAX_TOKENS: int = 2000
    TEMPERATURE: float = 0.7
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379"
    REDIS_MAX_CONNECTIONS: int = 10
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    LOG_FILE: Optional[Path] = PROJECT_ROOT / "logs" / "app.log"
    
    # Monitoring
    ENABLE_METRICS: bool = True
    METRICS_PORT: int = 9090
    
    # Rate Limiting
    RATE_LIMIT_REQUESTS: int = 50
    RATE_LIMIT_PERIOD: int = 60  # seconds
    
    # Vector Store
    VECTOR_DB_PATH: Path = PROJECT_ROOT / "data" / "vector_store"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True

@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings() 