"""Vector store management using ChromaDB (new API >= 0.4.x)"""

import chromadb
from typing import List, Dict, Any, Optional
from app.config import settings


class VectorStore:
    """ChromaDB vector store wrapper"""

    def __init__(self):
        """Initialize ChromaDB client using new persistent client API"""
        self.client = chromadb.PersistentClient(
            path=settings.CHROMA_PERSIST_DIRECTORY,
        )
        self.collection_name = "codebase_embeddings"
        self._collection = None

    def get_collection(self):
        """Get or create collection"""
        if self._collection is None:
            self._collection = self.client.get_or_create_collection(
                name=self.collection_name,
                metadata={"hnsw:space": "cosine"},
            )
        return self._collection

    def add_documents(
        self,
        documents: List[str],
        embeddings: List[List[float]],
        metadatas: List[Dict[str, Any]],
        ids: List[str],
    ):
        """Add documents to vector store"""
        collection = self.get_collection()
        collection.add(
            documents=documents,
            embeddings=embeddings,
            metadatas=metadatas,
            ids=ids,
        )

    def query(
        self,
        query_embedding: List[float],
        n_results: int = 5,
        where: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Query vector store"""
        collection = self.get_collection()
        kwargs: Dict[str, Any] = {
            "query_embeddings": [query_embedding],
            "n_results": n_results,
        }
        if where:
            kwargs["where"] = where
        return collection.query(**kwargs)

    def delete_workspace(self, workspace_id: str):
        """Delete all documents for a workspace"""
        collection = self.get_collection()
        try:
            results = collection.get(where={"workspace_id": workspace_id})
            if results["ids"]:
                collection.delete(ids=results["ids"])
        except Exception as e:
            print(f"Error deleting workspace documents: {e}")

    def get_workspace_count(self, workspace_id: str) -> int:
        """Get document count for a workspace"""
        collection = self.get_collection()
        try:
            results = collection.get(where={"workspace_id": workspace_id})
            return len(results["ids"])
        except Exception:
            return 0


# Global vector store instance
vector_store = VectorStore()
