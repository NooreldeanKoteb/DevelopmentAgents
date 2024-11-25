from typing import List, Dict, Any, Optional
import chromadb
from chromadb.config import Settings
import uuid

class VectorStore:
    """Manages vector storage and retrieval for embeddings."""
    
    def __init__(self):
        self.client = chromadb.Client(
            Settings(
                is_persistent=True,
                persist_directory="./data/chroma",
                anonymized_telemetry=False
            )
        )
        self.collections = {}
        self.initialized = False
        
    async def initialize(self):
        self.initialized = True
        
    async def cleanup(self):
        """Cleanup vector store resources."""
        for collection in self.collections.values():
            await collection.cleanup()
        self.collections.clear()
        self.initialized = False
        
    async def store_embeddings(
        self, 
        collection_name: str,
        texts: List[str],
        embeddings: List[List[float]],
        metadata: Optional[List[Dict[str, Any]]] = None
    ) -> None:
        """Store text embeddings with optional metadata."""
        collection = self.client.get_or_create_collection(collection_name)
        ids = [str(uuid.uuid4()) for _ in texts]
        collection.add(
            ids=ids,
            embeddings=embeddings,
            documents=texts,
            metadatas=metadata or [{} for _ in texts]
        )
        
    async def search(
        self,
        collection_name: str,
        query_embedding: List[float],
        n_results: int = 5
    ) -> List[Dict[str, Any]]:
        """Search for similar embeddings."""
        collection = self.client.get_collection(collection_name)
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results
        )
        return results 