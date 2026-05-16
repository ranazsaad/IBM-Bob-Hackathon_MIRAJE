"""VS Code integration routes"""

import os
import subprocess
from pathlib import Path
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.database.session import get_db
from app.database.models import Workspace
from app.config import settings

router = APIRouter(tags=["vscode"])


class CloneRepoRequest(BaseModel):
    """Request to clone a repository"""
    repo_url: str
    workspace_path: str = None


class OpenFileRequest(BaseModel):
    """Request to open a file in VS Code"""
    file_path: str
    workspace_path: str = None
    line_number: int = None


class VSCodeResponse(BaseModel):
    """VS Code operation response"""
    status: str
    message: str
    vscode_url: str = None
    workspace_path: str = None


@router.post("/clone-repo", response_model=VSCodeResponse)
async def clone_repo(
    request: CloneRepoRequest,
    db: Session = Depends(get_db)
):
    """
    Clone a GitHub repository to local workspace
    
    This creates a local copy that can be opened in VS Code
    """
    try:
        # Determine workspace path
        if request.workspace_path:
            workspace_path = Path(request.workspace_path)
        else:
            # Use default workspace directory
            workspace_path = Path.home() / "DevPilot-Workspaces"
        
        # Create workspace directory if it doesn't exist
        workspace_path.mkdir(parents=True, exist_ok=True)
        
        # Extract repo name from URL
        repo_name = request.repo_url.rstrip('/').split('/')[-1].replace('.git', '')
        repo_path = workspace_path / repo_name
        
        # Check if repo already exists
        if repo_path.exists():
            return VSCodeResponse(
                status="exists",
                message=f"Repository already cloned at {repo_path}",
                workspace_path=str(repo_path),
                vscode_url=f"vscode://file/{repo_path}"
            )
        
        # Clone the repository
        result = subprocess.run(
            ["git", "clone", request.repo_url, str(repo_path)],
            capture_output=True,
            text=True,
            timeout=300  # 5 minute timeout
        )
        
        if result.returncode != 0:
            raise HTTPException(
                status_code=500,
                detail=f"Git clone failed: {result.stderr}"
            )
        
        # Generate VS Code URL
        vscode_url = f"vscode://file/{repo_path}"
        
        return VSCodeResponse(
            status="success",
            message=f"Repository cloned successfully to {repo_path}",
            workspace_path=str(repo_path),
            vscode_url=vscode_url
        )
        
    except subprocess.TimeoutExpired:
        raise HTTPException(
            status_code=408,
            detail="Repository clone timed out. Repository may be too large."
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to clone repository: {str(e)}"
        )


@router.post("/open-file", response_model=VSCodeResponse)
async def open_file(request: OpenFileRequest):
    """
    Generate VS Code URL to open a specific file
    
    Supports opening at specific line numbers
    """
    try:
        # Construct file path
        if request.workspace_path:
            file_path = Path(request.workspace_path) / request.file_path
        else:
            file_path = Path(request.file_path)
        
        # Check if file exists
        if not file_path.exists():
            raise HTTPException(
                status_code=404,
                detail=f"File not found: {file_path}"
            )
        
        # Generate VS Code URL
        if request.line_number:
            vscode_url = f"vscode://file/{file_path}:{request.line_number}"
        else:
            vscode_url = f"vscode://file/{file_path}"
        
        return VSCodeResponse(
            status="success",
            message=f"VS Code URL generated for {file_path}",
            vscode_url=vscode_url,
            workspace_path=str(file_path.parent)
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate VS Code URL: {str(e)}"
        )


@router.get("/workspace-files")
async def list_workspace_files(workspace_path: str):
    """
    List all files in a workspace directory
    
    Returns file tree structure for display
    """
    try:
        workspace_path = Path(workspace_path)
        
        if not workspace_path.exists():
            raise HTTPException(
                status_code=404,
                detail=f"Workspace not found: {workspace_path}"
            )
        
        # Build file tree
        files = []
        for file_path in workspace_path.rglob("*"):
            if file_path.is_file():
                # Skip hidden files and common ignore patterns
                if any(part.startswith('.') for part in file_path.parts):
                    continue
                if any(ignore in str(file_path) for ignore in ['node_modules', '__pycache__', '.git']):
                    continue
                
                relative_path = file_path.relative_to(workspace_path)
                files.append({
                    "path": str(relative_path),
                    "full_path": str(file_path),
                    "size": file_path.stat().st_size,
                    "extension": file_path.suffix,
                })
        
        return {
            "workspace_path": str(workspace_path),
            "file_count": len(files),
            "files": sorted(files, key=lambda x: x["path"])
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to list workspace files: {str(e)}"
        )


@router.post("/open-workspace")
async def open_workspace(
    workspace_id: str,
    db: Session = Depends(get_db)
):
    """
    Open entire workspace in VS Code
    
    Clones repo if needed and opens in VS Code
    """
    try:
        # Get workspace from database
        workspace = db.query(Workspace).filter(Workspace.id == workspace_id).first()
        
        if not workspace:
            raise HTTPException(status_code=404, detail="Workspace not found")
        
        if workspace.type != "github":
            raise HTTPException(
                status_code=400,
                detail="Only GitHub workspaces can be opened in VS Code"
            )
        
        # Get repo URL from metadata
        repo_url = workspace.workspace_metadata.get("repo_url")
        if not repo_url:
            raise HTTPException(
                status_code=400,
                detail="Repository URL not found in workspace metadata"
            )
        
        # Clone repo
        clone_result = await clone_repo(
            CloneRepoRequest(repo_url=repo_url),
            db=db
        )
        
        return clone_result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to open workspace: {str(e)}"
        )


@router.get("/check-vscode")
async def check_vscode_installed():
    """
    Check if VS Code is installed on the system
    """
    try:
        # Try to run 'code --version'
        result = subprocess.run(
            ["code", "--version"],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if result.returncode == 0:
            version = result.stdout.split('\n')[0]
            return {
                "installed": True,
                "version": version,
                "message": "VS Code is installed and accessible"
            }
        else:
            return {
                "installed": False,
                "message": "VS Code command not found. Please install VS Code or add it to PATH."
            }
            
    except FileNotFoundError:
        return {
            "installed": False,
            "message": "VS Code is not installed or not in PATH"
        }
    except Exception as e:
        return {
            "installed": False,
            "message": f"Error checking VS Code: {str(e)}"
        }


# Made with IBM watsonx.ai

# Made with Bob
