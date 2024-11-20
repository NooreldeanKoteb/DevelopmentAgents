import pytest
from core.config import Settings, get_settings

def test_settings_defaults():
    """Test default settings values."""
    settings = Settings(OPENAI_API_KEY="dummy-key")  # Required field
    
    assert settings.ENVIRONMENT == "development"
    assert settings.DEBUG is False
    assert settings.OPENAI_MODEL == "gpt-4-turbo-preview"
    assert settings.TEMPERATURE == 0.7
    assert settings.MAX_TOKENS == 2000
    assert settings.RATE_LIMIT == 50
    assert settings.REDIS_URL == "redis://localhost:6379/0"
    assert settings.VECTOR_DB_PATH == "./data/vector_store"
    assert settings.LOG_LEVEL == "INFO"
    assert settings.PROMETHEUS_PORT == 9090

def test_settings_override():
    """Test settings override with custom values."""
    custom_settings = Settings(
        OPENAI_API_KEY="test-key",
        ENVIRONMENT="production",
        DEBUG=True,
        OPENAI_MODEL="gpt-3.5-turbo",
        TEMPERATURE=0.5,
        MAX_TOKENS=1000,
        RATE_LIMIT=30,
        REDIS_URL="redis://custom:6379/1",
        VECTOR_DB_PATH="/custom/path",
        LOG_LEVEL="DEBUG",
        PROMETHEUS_PORT=8080
    )
    
    assert custom_settings.ENVIRONMENT == "production"
    assert custom_settings.DEBUG is True
    assert custom_settings.OPENAI_API_KEY == "test-key"
    assert custom_settings.OPENAI_MODEL == "gpt-3.5-turbo"
    assert custom_settings.TEMPERATURE == 0.5
    assert custom_settings.MAX_TOKENS == 1000
    assert custom_settings.RATE_LIMIT == 30
    assert custom_settings.REDIS_URL == "redis://custom:6379/1"
    assert custom_settings.VECTOR_DB_PATH == "/custom/path"
    assert custom_settings.LOG_LEVEL == "DEBUG"
    assert custom_settings.PROMETHEUS_PORT == 8080

def test_get_settings_singleton():
    """Test that get_settings returns the same instance."""
    settings1 = get_settings()
    settings2 = get_settings()
    assert settings1 is settings2 