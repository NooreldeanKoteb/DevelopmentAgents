from .settings import Settings
from .monitoring import monitor_operation

_settings = None

def get_settings() -> Settings:
    """Get application settings singleton."""
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings

__all__ = ['Settings', 'get_settings', 'monitor_operation']
