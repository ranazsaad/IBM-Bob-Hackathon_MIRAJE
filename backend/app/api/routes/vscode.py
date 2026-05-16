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
from app.services.ibm_watsonx_client import AsyncIBMWatsonxClient
import json
import re

router = APIRouter(tags=["vscode"])


class CloneRepoRequest(BaseModel):
    """Request to clone a repository"""
    repo_url: str
    workspace_path: str = None


class ScaffoldProjectRequest(BaseModel):
    """Request to scaffold code for a full project"""
    workspace_id: str
    requirements: list = []
    tickets: list = []
    workspace_path: str = None


class OpenFileRequest(BaseModel):
    """Request to open a file in VS Code"""
    file_path: str
    workspace_path: str = None
    line_number: int = None


class DebugErrorRequest(BaseModel):
    """Request to debug an error"""
    workspace_id: str
    error_text: str


class VSCodeResponse(BaseModel):
    """VS Code operation response"""
    status: str
    message: str
    vscode_url: str = None
    workspace_path: str = None
    setup_guide: str = None


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


@router.post("/scaffold-project", response_model=VSCodeResponse)
async def scaffold_project(request: ScaffoldProjectRequest, db: Session = Depends(get_db)):
    """
    Generate files for a full project based on meeting requirements and save them to the workspace, then return VS Code URL
    """
    try:
        # Determine workspace path
        if request.workspace_path:
            workspace_path = Path(request.workspace_path)
        else:
            workspace_path = Path.home() / "DevPilot-Workspaces" / f"scaffold_{request.workspace_id}"
            
        workspace_path.mkdir(parents=True, exist_ok=True)
        
        reqs_str = "\n".join([f"- {r}" for r in request.requirements])
        tickets_str = "\n".join([f"Ticket: {t.get('title')}\nDesc: {t.get('description')}\n" for t in request.tickets])

        prompt = f"""You are an elite, senior software architect. A user wants to build a production-ready project based on these meeting requirements and tickets:

REQUIREMENTS:
{reqs_str}

TICKETS:
{tickets_str}

You MUST generate a complete, high-quality, working project structure from scratch that implements ALL of the above requirements and tickets. 
Adhere to the following STRICT guidelines:
1. Best Practices: Write clean, modular, and extremely high-quality code. Use modern frameworks, robust error handling, and standard architecture patterns.
2. Completeness: You must include ALL necessary boilerplate and configuration files (e.g., package.json, tsconfig.json, requirements.txt) and entry point files so the project runs out of the box without any missing dependencies.
3. README.md: You MUST generate a comprehensive `README.md` file in the root directory that contains EVERYTHING about the project (architecture, features, tech stack, setup instructions, and usage).
4. Do not omit any crucial code. Use descriptive variable names and helpful comments.
5. NO GIT CLONE: DO NOT include instructions to "git clone" a repository in the setup guide or README. The project files will be generated locally on the user's machine and opened directly in VS Code, so cloning is completely irrelevant.

Provide the full code for every file needed, AND a step-by-step setup guide.

Return your response ONLY as a single JSON object with the following structure:
{{
  "setup_guide": "Markdown formatted step-by-step instructions on how to install dependencies and run the project.",
  "files": [
    {{
      "path": "the relative file path (e.g., package.json, src/index.js)",
      "content": "the complete file content"
    }}
  ]
}}

IMPORTANT: You MUST properly escape all backslashes in your code content for JSON (e.g., write \\\\ instead of \\, \\\\n instead of \\n, \\\\d instead of \\d).
Do not include markdown formatting or any other text outside the JSON object."""

        client = AsyncIBMWatsonxClient()
        response = await client.chat.completions.create(
            model=settings.WATSONX_MODEL_ID,
            messages=[
                {"role": "system", "content": "You are a code generator. Always respond with valid JSON only."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.2,
            max_tokens=6000,
        )
        
        content = response.choices[0].message.content or "[]"
        content = re.sub(r"^```(?:json)?\s*", "", content, flags=re.MULTILINE)
        content = re.sub(r"\s*```$", "", content, flags=re.MULTILINE)
        
        try:
            result_data = json.loads(content, strict=False)
        except json.JSONDecodeError:
            # Fallback: attempt to fix invalid escapes that LLM missed
            fixed_content = re.sub(r'\\(?![/"\\bfnrtu])', r'\\\\', content)
            result_data = json.loads(fixed_content, strict=False)
        
        if not isinstance(result_data, dict) or "files" not in result_data:
            raise ValueError("LLM did not return the expected JSON object structure")
            
        files = result_data["files"]
        setup_guide = result_data.get("setup_guide", "No setup guide provided.")
            
        for file_obj in files:
            file_path = workspace_path / file_obj["path"]
            file_path.parent.mkdir(parents=True, exist_ok=True)
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(file_obj["content"])
                
        vscode_url = f"vscode://file/{workspace_path}"
        
        return VSCodeResponse(
            status="success",
            message=f"Scaffolded {len(files)} files successfully.",
            workspace_path=str(workspace_path),
            vscode_url=vscode_url,
            setup_guide=setup_guide
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to scaffold project: {str(e)}"
        )

@router.post("/debug-error")
async def debug_error(request: DebugErrorRequest, db: Session = Depends(get_db)):
    """
    Debug an error encountered in the scaffolded project
    """
    try:
        workspace_path = Path.home() / "DevPilot-Workspaces" / f"scaffold_{request.workspace_id}"
        
        # Read the files in the workspace to provide context to the LLM
        context_files = []
        if workspace_path.exists():
            for filepath in workspace_path.rglob("*"):
                if filepath.is_file() and not any(part.startswith('.') or part == 'node_modules' for part in filepath.parts):
                    try:
                        content = filepath.read_text(encoding="utf-8")
                        # limit file size to avoid huge tokens
                        if len(content) < 20000:
                            rel_path = filepath.relative_to(workspace_path)
                            context_files.append(f"--- {rel_path} ---\n{content}\n")
                    except Exception:
                        pass
                        
        files_context = "\n".join(context_files)
        
        prompt = f"""You are 'Bob', a helpful AI engineering teammate.
The user tried to run their project and encountered the following error in their terminal:

ERROR:
{request.error_text}

Here is the current code in their project:
{files_context}

Please analyze the error and the code, and tell the user EXACTLY what they need to do to fix the error and run the project successfully. Use clear, step-by-step markdown."""

        client = AsyncIBMWatsonxClient()
        response = await client.chat.completions.create(
            model=settings.WATSONX_MODEL_ID,
            messages=[
                {"role": "system", "content": "You are Bob, an expert software debugger. Keep your answers concise and directly address the error."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.2,
            max_tokens=2000,
        )
        
        return {"action": response.choices[0].message.content}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Made with IBM watsonx.ai

# Made with Bob
