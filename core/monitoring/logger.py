import logging
import json
from datetime import datetime
from typing import Any, Dict
from core.config import get_settings

class CoreLogger:
    """Structured logging for core components."""
    
    def __init__(self):
        settings = get_settings()
        self.logger = logging.getLogger("core")
        self.logger.setLevel(settings.LOG_LEVEL)
        
        # Add JSON handler
        handler = logging.StreamHandler()
        handler.setFormatter(self.JsonFormatter())
        self.logger.addHandler(handler)
        
    class JsonFormatter(logging.Formatter):
        def format(self, record: logging.LogRecord) -> str:
            log_data = {
                "timestamp": datetime.utcnow().isoformat(),
                "level": record.levelname,
                "message": record.getMessage(),
                "module": record.module,
                "function": record.funcName
            }
            
            if hasattr(record, "extra"):
                log_data.update(record.extra)
                
            return json.dumps(log_data) 