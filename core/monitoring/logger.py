import logging
import json
from datetime import datetime
from typing import Any, Dict
from core.config import get_settings

class CoreLogger:
    """Core system logger."""
    
    def __init__(self):
        self.logger = logging.getLogger("core")
        self.logger.setLevel(logging.INFO)
        
        # Ensure propagation to root logger (needed for caplog)
        self.logger.propagate = True
        
        # Remove any existing handlers to prevent duplicates
        self.logger.handlers = []
        
        # Add console handler
        handler = logging.StreamHandler()
        handler.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
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