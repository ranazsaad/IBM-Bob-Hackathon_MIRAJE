"""RAG (Retrieval Augmented Generation) Engine"""

from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session

from app.database.vector_store import vector_store
from app.services.embedding_service import embedding_service
from app.database.models import Workspace, File


class RAGEngine:
    """RAG engine for context retrieval"""
    
    def __init__(self, db: Session):
        """Initialize RAG engine"""
        self.db = db
        self.vector_store = vector_store
        self.embedding_service = embedding_service
    
    async def retrieve_context(
        self,
        query: str,
        workspace_id: str,
        top_k: int = 5,
        file_path: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Retrieve relevant context for a query
        
        Args:
            query: User query
            workspace_id: Workspace ID
            top_k: Number of results to retrieve
            file_path: Optional specific file to search in
            
        Returns:
            Dictionary with retrieved chunks and metadata
        """
        try:
            # Get workspace
            workspace = self.db.query(Workspace).filter(
                Workspace.id == workspace_id
            ).first()
            
            if not workspace:
                raise ValueError(f"Workspace {workspace_id} not found")
            
            # Generate query embedding
            query_embedding = await self.embedding_service.generate_embedding(query)
            
            # Build where clause for filtering
            where_clause = {"workspace_id": workspace_id}
            if file_path:
                where_clause["file_path"] = file_path
            
            # Query vector store
            results = self.vector_store.query(
                query_embedding=query_embedding,
                n_results=top_k,
                where=where_clause
            )
            
            # Format results
            chunks = []
            if results and results.get("documents"):
                for i, doc in enumerate(results["documents"][0]):
                    metadata = results["metadatas"][0][i] if results.get("metadatas") else {}
                    distance = results["distances"][0][i] if results.get("distances") else 0
                    
                    chunks.append({
                        "content": doc,
                        "metadata": metadata,
                        "relevance_score": 1 - distance,  # Convert distance to similarity
                    })
            
            # Get workspace metadata for context
            workspace_context = {
                "type": workspace.type,
                "metadata": workspace.workspace_metadata or {},
            }
            
            return {
                "chunks": chunks,
                "workspace_context": workspace_context,
                "total_retrieved": len(chunks),
            }
            
        except Exception as e:
            print(f"Error retrieving context: {e}")
            return {
                "chunks": [],
                "workspace_context": {},
                "total_retrieved": 0,
                "error": str(e)
            }
    
    async def get_file_content(
        self,
        workspace_id: str,
        file_path: str
    ) -> Optional[str]:
        """Get full content of a specific file"""
        try:
            file = self.db.query(File).filter(
                File.workspace_id == workspace_id,
                File.file_path == file_path
            ).first()
            
            return file.content if file else None
            
        except Exception as e:
            print(f"Error getting file content: {e}")
            return None
    
    def get_workspace_summary(self, workspace_id: str) -> Dict[str, Any]:
        """Get summary of workspace for context"""
        try:
            workspace = self.db.query(Workspace).filter(
                Workspace.id == workspace_id
            ).first()
            
            if not workspace:
                return {}
            
            file_count = self.db.query(File).filter(
                File.workspace_id == workspace_id
            ).count()
            
            indexed_count = self.db.query(File).filter(
                File.workspace_id == workspace_id,
                File.indexed == True
            ).count()
            
            return {
                "type": workspace.type,
                "metadata": workspace.workspace_metadata or {},
                "file_count": file_count,
                "indexed_count": indexed_count,
                "created_at": workspace.created_at.isoformat() if workspace.created_at else None,
            }
            
        except Exception as e:
            print(f"Error getting workspace summary: {e}")
            return {}

# Made with Bob
