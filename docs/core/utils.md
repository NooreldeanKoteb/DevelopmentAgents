



# Core Utils Documentation

## Overview
The utils module provides common utility functions and helpers used throughout the application. It includes async utilities, security helpers, data processing functions, and other shared tools.

## Key Components

### 1. Async Utilities
**Location**: `core/utils/async_utils.py`

Helper functions for async operations.

**Key Features**:
- Task management
- Concurrency control
- Async patterns
- Timeout handling
- Rate limiting

```python
from core.utils.async_utils import AsyncUtils

async def with_timeout(coro, timeout=5.0):
    try:
        return await asyncio.wait_for(coro, timeout)
    except asyncio.TimeoutError:
        raise TimeoutError(f"Operation timed out after {timeout}s")
```


### 2. Security Utils
**Location**: `core/utils/security.py`

Security-related utility functions.

**Key Features**:
- Hashing functions
- Encryption helpers
- Token management
- Input sanitization
- Security validation

```python
from core.utils.security import SecurityUtils

# Hash sensitive data
hashed = SecurityUtils.hash_password(password)

# Validate input
cleaned = SecurityUtils.sanitize_input(user_input)
```


### 3. Data Processing
**Location**: `core/utils/data.py`

Data manipulation and processing utilities.

```python
class DataUtils:
    @staticmethod
    def chunk_list(items: List[Any], size: int) -> List[List[Any]]:
        """Split list into chunks of specified size."""
        return [items[i:i + size] for i in range(0, len(items), size)]
        
    @staticmethod
    def flatten_dict(d: Dict, parent_key: str = '', sep: str = '.') -> Dict:
        """Flatten nested dictionary with dot notation."""
        items: List = []
        for k, v in d.items():
            new_key = f"{parent_key}{sep}{k}" if parent_key else k
            if isinstance(v, dict):
                items.extend(
                    DataUtils.flatten_dict(v, new_key, sep=sep).items()
                )
            else:
                items.append((new_key, v))
        return dict(items)
```


## Common Utilities

### 1. Time Utilities
```python
class TimeUtils:
    @staticmethod
    def parse_duration(duration_str: str) -> timedelta:
        """Parse duration string (e.g., '1h30m') into timedelta."""
        pattern = re.compile(r'(\d+)([dhms])')
        parts = pattern.findall(duration_str)
        time_dict = {'d': 0, 'h': 0, 'm': 0, 's': 0}
        
        for value, unit in parts:
            time_dict[unit] = int(value)
            
        return timedelta(
            days=time_dict['d'],
            hours=time_dict['h'],
            minutes=time_dict['m'],
            seconds=time_dict['s']
        )
```


### 2. Validation Utils
```python
class ValidationUtils:
    @staticmethod
    def is_valid_email(email: str) -> bool:
        """Validate email format."""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))
        
    @staticmethod
    def is_valid_uuid(uuid_str: str) -> bool:
        """Validate UUID format."""
        try:
            UUID(uuid_str)
            return True
        except ValueError:
            return False
```


### 3. File Utils
```python
class FileUtils:
    @staticmethod
    async def read_file_chunks(
        path: str,
        chunk_size: int = 8192
    ) -> AsyncGenerator[bytes, None]:
        """Read file in chunks asynchronously."""
        async with aiofiles.open(path, 'rb') as f:
            while chunk := await f.read(chunk_size):
                yield chunk
                
    @staticmethod
    async def ensure_directory(path: str) -> None:
        """Ensure directory exists."""
        os.makedirs(path, exist_ok=True)
```


## Decorators

### 1. Retry Decorator
```python
def retry(
    max_attempts: int = 3,
    delay: float = 1.0,
    backoff: float = 2.0,
    exceptions: Tuple[Type[Exception], ...] = (Exception,)
):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            attempt = 0
            current_delay = delay
            
            while attempt < max_attempts:
                try:
                    return await func(*args, **kwargs)
                except exceptions as e:
                    attempt += 1
                    if attempt == max_attempts:
                        raise
                    await asyncio.sleep(current_delay)
                    current_delay *= backoff
            
        return wrapper
    return decorator
```


### 2. Cache Decorator
```python
def cached(ttl: int = 300):
    def decorator(func):
        cache = {}
        
        @wraps(func)
        async def wrapper(*args, **kwargs):
            key = str(args) + str(kwargs)
            now = time.time()
            
            if key in cache:
                result, timestamp = cache[key]
                if now - timestamp < ttl:
                    return result
                    
            result = await func(*args, **kwargs)
            cache[key] = (result, now)
            return result
            
        return wrapper
    return decorator
```


## Error Handling

```python
class UtilsError(Exception):
    """Base class for utility errors"""
    pass

class ValidationError(UtilsError):
    """Validation error"""
    pass

class TimeoutError(UtilsError):
    """Timeout error"""
    pass
```


## Common Usage Patterns

### 1. Async Batch Processing
```python
async def process_batch(items: List[Any], batch_size: int = 100):
    for batch in DataUtils.chunk_list(items, batch_size):
        tasks = [process_item(item) for item in batch]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for item, result in zip(batch, results):
            if isinstance(result, Exception):
                logger.error(f"Failed to process {item}: {result}")
```


### 2. Safe Data Access
```python
def safe_get(obj: Any, path: str, default: Any = None) -> Any:
    """Safely get nested dictionary values."""
    try:
        for key in path.split('.'):
            obj = obj[key]
        return obj
    except (KeyError, TypeError, AttributeError):
        return default
```


### 3. Rate Limiting
```python
class RateLimiter:
    def __init__(self, rate: int, per: float = 1.0):
        self.rate = rate
        self.per = per
        self.allowance = rate
        self.last_check = time.time()
        
    async def acquire(self) -> bool:
        """Check if operation is allowed under rate limit."""
        current = time.time()
        time_passed = current - self.last_check
        self.last_check = current
        self.allowance += time_passed * (self.rate / self.per)
        
        if self.allowance > self.rate:
            self.allowance = self.rate
            
        if self.allowance < 1:
            return False
            
        self.allowance -= 1
        return True
```


## Testing

```python
async def test_retry_decorator():
    attempts = 0
    
    @retry(max_attempts=3, delay=0.1)
    async def failing_function():
        nonlocal attempts
        attempts += 1
        raise ValueError("Test error")
        
    with pytest.raises(ValueError):
        await failing_function()
        
    assert attempts == 3
```


## Development Guidelines

1. Keep utilities focused and simple
2. Document all utility functions
3. Include proper error handling
4. Add appropriate type hints
5. Write comprehensive tests
6. Consider performance implications
7. Maintain backward compatibility

For more detailed examples and advanced usage patterns, refer to the tests in `tests/core/utils/`.

Remember to:
- Keep utilities generic
- Avoid duplicating functionality
- Document edge cases
- Consider async implications
- Test thoroughly
- Monitor performance
