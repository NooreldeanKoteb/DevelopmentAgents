import pytest
from core.config.settings import Settings, Environment

def test_settings_creation():
    settings = Settings()
    assert settings.ENVIRONMENT == Environment.DEVELOPMENT
    assert settings.DEBUG is True

def test_settings_defaults():
    settings = Settings()
    assert settings.REDIS_URL == "redis://localhost:6379/0"
    assert settings.PROMETHEUS_PORT == 9090