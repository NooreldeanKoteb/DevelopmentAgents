import logging
import json
from typing import Any, Dict

class JsonFormatter(logging.Formatter):
    """Custom JSON formatter."""
    def format(self, record):
        # First call the parent class's format to get the message
        record.message = record.getMessage()
        
        log_data = {
            "timestamp": self.formatTime(record),
            "level": record.levelname,
            "message": record.message,
            "data": getattr(record, 'data', {})
        }
        return json.dumps(log_data)

class CoreLogger:
    """Core logging functionality with JSON formatting."""
    
    def __init__(self):
        """Initialize logger with JSON formatter."""
        self.logger = logging.getLogger("core")
        self.formatter = JsonFormatter()
        
        # Add handler if none exists
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            handler.setFormatter(self.formatter)
            self.logger.addHandler(handler)
    
    def _format_extra(self, extra: Dict[str, Any] = None) -> Dict[str, Any]:
        """Format extra data for JSON logging."""
        return extra if extra is not None else {}
    
    def info(self, message: str, extra: Dict[str, Any] = None):
        """Log info message with JSON formatting."""
        self.logger.info(message, extra={"data": self._format_extra(extra)})
    
    def error(self, message: str, extra: Dict[str, Any] = None):
        """Log error message with JSON formatting."""
        self.logger.error(message, extra={"data": self._format_extra(extra)})
    
    def warning(self, message: str, extra: Dict[str, Any] = None):
        """Log warning message with JSON formatting."""
        self.logger.warning(message, extra={"data": self._format_extra(extra)})