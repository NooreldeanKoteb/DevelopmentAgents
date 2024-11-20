from typing import List, Dict, Any, Optional
import chromadb
from chromadb.config import Settings
from core.config import get_settings

class VectorStore:
    """Manages vector storage and retrieval for embeddings."""
    
    def __init__(self):
        settings = get_settings()
        self.client = chromadb.Client(Settings(
            chroma_db_impl="duckdb+parquet",
            persist_directory=settings.VECTOR_DB_PATH
        ))
        
    async def store_embeddings(
        self, 
        collection_name: str,
        texts: List[str],
        embeddings: List[List[float]],
        metadata: Optional[List[Dict[str, Any]]] = None
    ) -> None:
        """Store text embeddings with optional metadata."""
        collection = self.client.get_or_create_collection(collection_name)
        collection.add(
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