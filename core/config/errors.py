from typing import Optional, Dict, Any
from dataclasses import dataclass
from datetime import datetime

@dataclass
class AppError(Exception):
    """Base error class for the application."""
    message: str
    code: str
    details: Optional[Dict[str, Any]] = None
    timestamp: datetime = datetime.utcnow()

class ConfigError(AppError):
    """Configuration related errors."""
    pass

class APIError(AppError):
    """API related errors."""
    pass

class AgentError(AppError):
    """Agent related errors."""
    pass

class DatabaseError(AppError):
    """Database related errors."""
    pass

def handle_error(error: AppError) -> Dict[str, Any]:
    """Global error handler."""
    error_data = {
        "error": {
            "code": error.code,
            "message": error.message,
            "timestamp": error.timestamp.isoformat(),
            "type": error.__class__.__name__
        }
    }
    
    if error.details:
        error_data["error"]["details"] = error.details
    
    return error_data 