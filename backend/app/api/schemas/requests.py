"""Request schemas"""

from pydantic import BaseModel, Field, HttpUrl
from typing import Optional, Dict, Any


class GitHubAnalyzeRequest(BaseModel):
    """Request schema for GitHub repository analysis"""
    
    repo_url: HttpUrl = Field(..., description="GitHub repository URL")
    branch: str = Field(default="main", description="Branch to analyze")
    depth: str = Field(default="shallow", description="Analysis depth: shallow or deep")
    
    class Config:
        json_schema_extra = {
            "example": {
                "repo_url": "https://github.com/user/repo",
                "branch": "main",
                "depth": "shallow"
            }
        }


class TranscriptAnalyzeRequest(BaseModel):
    """Request schema for meeting transcript analysis"""
    
    transcript: str = Field(..., description="Meeting transcript text")
    context: Optional[str] = Field(None, description="Additional context")
    
    class Config:
        json_schema_extra = {
            "example": {
                "transcript": "Meeting notes discussing new features...",
                "context": "Sprint planning for Q2"
            }
        }


class ModeQueryRequest(BaseModel):
    """Request schema for AI mode queries"""
    
    workspace_id: str = Field(..., description="Workspace ID")
    query: str = Field(..., description="User query")
    context: Optional[Dict[str, Any]] = Field(None, description="Additional context")
    
    class Config:
        json_schema_extra = {
            "example": {
                "workspace_id": "uuid-here",
                "query": "Generate unit tests for the authentication module",
                "context": {
                    "file_path": "src/auth.py"
                }
            }
        }

# Made with Bob
