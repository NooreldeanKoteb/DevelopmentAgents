

# Core Storage System Documentation

## Overview
The storage system provides a unified interface for data persistence, caching, and retrieval across different storage backends. It supports vector storage, message persistence, and general data storage with async operations.

## Key Components

### 1. Vector Store
**Location**: `core/storage/vector_db.py`

Manages vector embeddings storage and similarity search.

**Key Features**:
- Vector storage and retrieval
- Similarity search
- Metadata management
- Collection management
- Batch operations

```python
from core.storage import VectorStore

vector_store = VectorStore()
await vector_store.store(
    vectors=[embedding],
    metadata=[{"text": "sample text", "type": "document"}],
    collection="documents"
)
```

### 2. Message Store
**Location**: `core/storage/message_store.py`

Handles persistent storage of system messages.

**Key Features**:
- Message persistence
- Time-based queries
- Topic-based retrieval
- Message expiration
- Batch operations

```python
from core.storage import MessageStore

message_store = MessageStore()
await message_store.store_message(message)
messages = await message_store.get_messages(
    topic="user.events",
    start_time=datetime.now() - timedelta(hours=1)
)
```

### 3. Cache System
**Location**: `core/storage/cache.py`

Manages application caching with Redis.

**Key Features**:
- Key-value storage
- TTL management
- Pattern matching
- Atomic operations
- Pub/sub support

```python
from core.storage import CacheManager

cache = CacheManager()
await cache.set("user:123", user_data, ttl=3600)
user = await cache.get("user:123")
```

## Storage Interfaces

### 1. Base Storage Interface
```python
class BaseStorage(ABC):
    @abstractmethod
    async def store(self, key: str, data: Any) -> bool:
        pass
        
    @abstractmethod
    async def retrieve(self, key: str) -> Optional[Any]:
        pass
        
    @abstractmethod
    async def delete(self, key: str) -> bool:
        pass
        
    @abstractmethod
    async def exists(self, key: str) -> bool:
        pass
```

### 2. Vector Storage Interface
```python
class VectorStorageInterface(BaseStorage):
    async def store_vectors(
        self, 
        vectors: List[List[float]], 
        metadata: List[Dict[str, Any]]
    ) -> List[str]:
        pass
        
    async def search_similar(
        self, 
        query_vector: List[float], 
        k: int = 5
    ) -> List[SearchResult]:
        pass
```

## Common Operations

### 1. Vector Operations
```python
async def store_document_embedding(
    text: str,
    embedding: List[float],
    metadata: Dict[str, Any]
):
    await vector_store.add_vectors(
        collection="documents",
        vectors=[embedding],
        metadata=[{
            "text": text,
            **metadata
        }]
    )
```

### 2. Message Operations
```python
async def store_system_event(event: SystemEvent):
    await message_store.store_message(
        Message(
            topic="system.events",
            content=event.dict(),
            timestamp=datetime.utcnow()
        )
    )
```

### 3. Cache Operations
```python
async def cached_operation(key: str, operation: Callable):
    # Try cache first
    result = await cache.get(key)
    if result is not None:
        return result
        
    # Execute operation and cache
    result = await operation()
    await cache.set(key, result, ttl=3600)
    return result
```

## Error Handling

```python
class StorageError(Exception):
    """Base storage error"""
    pass

class VectorStoreError(StorageError):
    """Vector storage specific errors"""
    pass

class CacheError(StorageError):
    """Cache operation errors"""
    pass

class MessageStoreError(StorageError):
    """Message storage errors"""
    pass
```

## Best Practices

### 1. Vector Store Usage
```python
async def search_similar_documents(query_vector: List[float]):
    try:
        results = await vector_store.search(
            collection="documents",
            query_vector=query_vector,
            k=5,
            min_similarity=0.7
        )
        return [result.metadata for result in results]
    except VectorStoreError as e:
        logger.error(f"Vector search failed: {e}")
        raise
```

### 2. Cache Management
```python
async def manage_cache():
    # Set with TTL
    await cache.set_nx("lock:process", "1", ttl=60)
    
    # Atomic operations
    await cache.increment("counter:requests")
    
    # Pattern deletion
    await cache.delete_pattern("user:*:session")
```

### 3. Message Storage
```python
async def handle_message_storage(message: Message):
    # Store with TTL
    await message_store.store(
        message,
        ttl=timedelta(days=7)
    )
    
    # Cleanup old messages
    await message_store.cleanup_old_messages(
        older_than=timedelta(days=30)
    )
```

## Performance Optimization

### 1. Batch Operations
```python
async def batch_vector_store(vectors: List[List[float]]):
    for batch in chunks(vectors, size=100):
        await vector_store.add_vectors(batch)
```

### 2. Cache Strategies
```python
class CacheStrategy:
    @staticmethod
    async def cached_query(query_key: str, query_func: Callable):
        cached = await cache.get(query_key)
        if cached:
            return cached
            
        result = await query_func()
        await cache.set(query_key, result, ttl=300)
        return result
```

## Monitoring Integration

```python
@metrics.track_storage_operation
async def monitored_storage_operation():
    start_time = time.time()
    try:
        await store_operation()
        metrics.observe(
            "storage_operation_duration",
            time.time() - start_time
        )
    except StorageError:
        metrics.increment("storage_errors_total")
        raise
```

## Testing

```python
async def test_vector_store():
    store = VectorStore()
    
    # Test storage
    vector = [0.1] * 128
    id = await store.add_vector(vector)
    assert id is not None
    
    # Test retrieval
    result = await store.get_vector(id)
    assert np.allclose(result, vector)
    
    # Test search
    results = await store.search_similar(vector, k=1)
    assert len(results) == 1
```

## Common Use Cases

### 1. Document Storage
```python
async def store_document(document: Document):
    # Store text embedding
    embedding = await get_embedding(document.text)
    await vector_store.add(
        vectors=[embedding],
        metadata=[{
            "doc_id": document.id,
            "text": document.text,
            "type": document.type
        }]
    )
```

### 2. Session Management
```python
async def manage_session(session_id: str, data: Dict):
    await cache.set(
        f"session:{session_id}",
        data,
        ttl=3600  # 1 hour
    )
```

### 3. Event Storage
```python
async def store_event(event: Event):
    await message_store.store(
        Message(
            topic=f"events.{event.type}",
            content=event.dict(),
            timestamp=event.timestamp
        )
    )
```

## Development Guidelines

1. Use appropriate storage for data types
2. Implement proper error handling
3. Monitor storage operations
4. Implement cleanup strategies
5. Use batch operations when possible
6. Maintain proper indexing
7. Regular maintenance tasks

For more detailed examples and advanced usage patterns, refer to the tests in `tests/core/storage/`.

Remember to:
- Monitor storage usage
- Implement backup strategies
- Handle storage errors gracefully
- Optimize query patterns
- Maintain data consistency
