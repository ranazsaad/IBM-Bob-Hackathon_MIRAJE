"""Workspace management endpoints"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.database.session import get_db
from app.database.models import Workspace, File
from app.api.schemas.responses import WorkspaceResponse, FileResponse

router = APIRouter()


@router.get("/{workspace_id}", response_model=WorkspaceResponse)
async def get_workspace(
    workspace_id: str,
    db: Session = Depends(get_db)
):
    """Get workspace details"""
    workspace = db.query(Workspace).filter(Workspace.id == workspace_id).first()
    
    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace not found")
    
    file_count = db.query(File).filter(File.workspace_id == workspace_id).count()
    
    return WorkspaceResponse(
        workspace_id=workspace.id,
        type=workspace.type,
        metadata=workspace.workspace_metadata or {},
        created_at=workspace.created_at,
        last_accessed=workspace.last_accessed,
        file_count=file_count
    )


@router.get("/{workspace_id}/files", response_model=List[FileResponse])
async def get_workspace_files(
    workspace_id: str,
    db: Session = Depends(get_db)
):
    """Get all files in a workspace"""
    workspace = db.query(Workspace).filter(Workspace.id == workspace_id).first()
    
    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace not found")
    
    files = db.query(File).filter(File.workspace_id == workspace_id).all()
    
    return [
        FileResponse(
            path=file.file_path,
            language=file.language,
            lines=file.lines,
            indexed=file.indexed
        )
        for file in files
    ]


@router.delete("/{workspace_id}")
async def delete_workspace(
    workspace_id: str,
    db: Session = Depends(get_db)
):
    """Delete a workspace and all associated data"""
    workspace = db.query(Workspace).filter(Workspace.id == workspace_id).first()
    
    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace not found")
    
    # Delete from vector store
    from app.database.vector_store import vector_store
    vector_store.delete_workspace(workspace_id)
    
    # Delete from database (cascade will handle files and queries)
    db.delete(workspace)
    db.commit()
    
    return {"message": "Workspace deleted successfully"}

# Made with Bob
