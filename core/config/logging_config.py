import logging
import sys
from pathlib import Path
from logging.handlers import RotatingFileHandler
from .settings import get_settings

def setup_logging():
    """Configure the logging system."""
    settings = get_settings()
    
    # Create logs directory if it doesn't exist
    if settings.LOG_FILE:
        settings.LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(settings.LOG_LEVEL)
    
    # Create formatters
    formatter = logging.Formatter(settings.LOG_FORMAT)
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)
    
    # File handler (if LOG_FILE is set)
    if settings.LOG_FILE:
        file_handler = RotatingFileHandler(
            settings.LOG_FILE,
            maxBytes=10_000_000,  # 10MB
            backupCount=5
        )
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)
    
    # Set logging levels for third-party packages
    logging.getLogger("asyncio").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING) 