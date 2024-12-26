

# Core Configuration System Documentation

## Overview
The configuration system manages application settings, constants, and environment variables. It provides a centralized way to handle configuration across the entire application with type safety and validation.

## Key Components

### 1. Settings Class
**Location**: `core/config/settings.py`

The main configuration class using Pydantic for validation.

**Key Features**:
- Environment variable loading
- Type validation
- Default values
- Nested configuration support
- Secret handling

**Usage Example**:
```python
from core.config import Settings

settings = Settings()
database_url = settings.database.url
api_key = settings.api.key
```

### 2. Constants
**Location**: `core/config/constants.py`

System-wide constants and configuration values.

**Common Constants**:
```python
# System limits
MAX_RETRY_ATTEMPTS = 3
DEFAULT_TIMEOUT = 30
MAX_QUEUE_SIZE = 1000

# File paths
CONFIG_PATH = "config/"
CACHE_PATH = "cache/"
LOG_PATH = "logs/"

# API Settings
API_VERSION = "v1"
DEFAULT_PAGE_SIZE = 50
```

### 3. Environment Configuration
**Location**: `core/config/environment.py`

Handles different environment configurations (development, testing, production).

**Key Features**:
- Environment detection
- Environment-specific settings
- Configuration overrides
- Secret management

**Usage Example**:
```python
from core.config import get_environment_config

config = get_environment_config()
debug_mode = config.debug
log_level = config.log_level
```

### 4. Validation Rules
**Location**: `core/config/validation.py`

Defines validation rules and constraints for configuration values.

**Example Rules**:
```python
class DatabaseConfig(BaseConfig):
    url: str
    max_connections: int = Field(ge=1, le=100)
    timeout: int = Field(ge=0, le=300)
    retry_attempts: int = Field(ge=0, le=5)
```

## Configuration Structure

1. **Base Configuration**:
```python
class BaseConfig(BaseSettings):
    class Config:
        env_file = ".env"
        case_sensitive = True
```

2. **API Configuration**:
```python
class APIConfig(BaseConfig):
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = False
    cors_origins: List[str] = ["*"]
```

3. **Database Configuration**:
```python
class DatabaseConfig(BaseConfig):
    url: str
    pool_size: int = 5
    ssl_mode: Optional[str] = None
    echo: bool = False
```

## Best Practices

1. **Loading Configuration**:
```python
from core.config import Settings

settings = Settings()
if settings.debug:
    configure_debug_logging()
```

2. **Environment Variables**:
```python
# .env file
DATABASE_URL=postgresql://user:pass@localhost/db
API_KEY=secret_key
DEBUG=True

# Usage
database_url = settings.database.url  # Type-safe, validated
```

3. **Configuration Updates**:
```python
async def update_config():
    await settings.refresh()  # Reload from environment
    notify_services_of_config_change()
```

## Error Handling

Custom error types:
- ConfigError: Base configuration error
- ValidationError: Configuration validation errors
- EnvironmentError: Environment loading errors
- SecretError: Secret management errors

## Security Considerations

1. **Secret Management**:
- Never log sensitive values
- Use secret management services
- Encrypt sensitive configuration
- Rotate secrets regularly

2. **Access Control**:
- Restrict configuration access
- Audit configuration changes
- Validate configuration updates

## Testing

The system includes tests for:
- Configuration loading
- Validation rules
- Environment detection
- Secret handling
- Configuration updates

**Example Test**:
```python
def test_database_config():
    settings = Settings()
    assert settings.database.url.startswith("postgresql://")
    assert 1 <= settings.database.pool_size <= 20
```

## Common Usage Patterns

1. **Service Configuration**:
```python
@dataclass
class ServiceConfig:
    def __init__(self):
        settings = Settings()
        self.timeout = settings.service.timeout
        self.retry_count = settings.service.retry_count
```

2. **Feature Flags**:
```python
def is_feature_enabled(feature_name: str) -> bool:
    return settings.features.get(feature_name, False)
```

3. **Dynamic Configuration**:
```python
async def get_dynamic_config():
    config = await redis.get("app:config")
    return Settings.parse_raw(config)
```

## Integration Points

The configuration system integrates with:
1. Environment variables
2. Secret management services
3. Configuration files
4. Dynamic configuration stores
5. Monitoring systems

## Monitoring

Configuration monitoring includes:
- Configuration change tracking
- Validation error reporting
- Access logging
- Performance impact tracking

## Development Guidelines

1. Always use type hints
2. Document all configuration options
3. Provide sensible defaults
4. Include validation rules
5. Handle configuration errors gracefully
6. Monitor configuration usage
7. Maintain backward compatibility

For more detailed examples and advanced usage patterns, refer to the tests in `tests/core/config/`.
