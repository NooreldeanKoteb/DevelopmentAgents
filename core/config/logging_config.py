import logging
import logging.config
from core.config.settings import get_settings

def setup_logging() -> None:
    """Configure logging based on settings."""
    settings = get_settings()
    
    log_config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "standard": {
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            },
            "json": {
                "format": "%(asctime)s %(name)s %(levelname)s %(message)s"
            }
        },
        "handlers": {
            "default": {
                "level": settings.LOG_LEVEL,
                "formatter": settings.LOG_FORMAT,
                "class": "logging.StreamHandler",
                "stream": "ext://sys.stdout",
            }
        },
        "loggers": {
            "": {
                "handlers": ["default"],
                "level": settings.LOG_LEVEL,
                "propagate": True
            }
        }
    }
    
    logging.config.dictConfig(log_config)
    
    # Set logging levels for third-party packages
    logging.getLogger("asyncio").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)  