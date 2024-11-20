import pytest
import numpy as np
from core.storage.vector_db import VectorStore

@pytest.fixture
async def vector_store():
    store = VectorStore()
    yield store
    # Cleanup collections after tests
    for collection in store.client.list_collections():
        store.client.delete_collection(collection.name)

@pytest.mark.asyncio
async def test_store_and_retrieve_embeddings(vector_store):
    """Test storing and retrieving embeddings."""
    # Create test data
    texts = ["test document 1", "test document 2"]
    embeddings = [
        np.random.rand(384).tolist(),  # Using 384 dimensions as example
        np.random.rand(384).tolist()
    ]
    metadata = [
        {"source": "test1"},
        {"source": "test2"}
    ]
    
    # Store embeddings
    await vector_store.store_embeddings(
        "test_collection",
        texts,
        embeddings,
        metadata
    )
    
    # Search with first embedding
    results = await vector_store.search(
        "test_collection",
        embeddings[0],
        n_results=1
    )
    
    assert len(results['documents']) == 1
    assert results['documents'][0][0] == texts[0]
    assert results['metadatas'][0][0]['source'] == "test1" 