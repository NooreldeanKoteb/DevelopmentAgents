import pytest
from core.config.settings import Settings, Environment

def test_settings_creation():
    """Test basic settings creation."""
    settings = Settings(
        OPENAI_API_KEY="dummy-key",
        _env_file=None,
        DEBUG=False
    )
    assert settings.ENVIRONMENT == Environment.DEVELOPMENT
    assert settings.DEBUG is False  # Explicitly check for False

def test_settings_defaults():
    """Test default settings values."""
    settings = Settings(
        OPENAI_API_KEY="dummy-key",
        _env_file=None
    )
    assert settings.REDIS_URL == "redis://localhost:6379/0"
    assert settings.PROMETHEUS_PORT == 9090
    assert settings.SERVER_PORT == 8000