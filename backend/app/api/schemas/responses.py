"""Response schemas"""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime


class HealthResponse(BaseModel):
    """Health check response"""
    
    status: str = Field(..., description="Service status")
    version: str = Field(..., description="API version")
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class GitHubAnalyzeResponse(BaseModel):
    """Response schema for GitHub repository analysis"""
    
    workspace_id: str = Field(..., description="Workspace ID")
    status: str = Field(..., description="Analysis status")
    metadata: Dict[str, Any] = Field(..., description="Repository metadata")
    indexed_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_schema_extra = {
            "example": {
                "workspace_id": "uuid-here",
                "status": "completed",
                "metadata": {
                    "repo_name": "example-repo",
                    "language": "Python",
                    "file_count": 45,
                    "total_lines": 12500
                },
                "indexed_at": "2026-05-15T22:00:00Z"
            }
        }


class TranscriptAnalyzeResponse(BaseModel):
    """Response schema for transcript analysis"""
    
    workspace_id: str = Field(..., description="Workspace ID")
    status: str = Field(..., description="Analysis status")
    extracted_data: Dict[str, Any] = Field(..., description="Extracted data")
    
    class Config:
        json_schema_extra = {
            "example": {
                "workspace_id": "uuid-here",
                "status": "completed",
                "extracted_data": {
                    "requirements": ["Feature A", "Feature B"],
                    "user_stories": [],
                    "tickets": []
                }
            }
        }


class ModeQueryResponse(BaseModel):
    """Response schema for AI mode queries"""
    
    mode: str = Field(..., description="AI mode used")
    result: Dict[str, Any] = Field(..., description="Query result")
    suggestions: Optional[List[str]] = Field(None, description="Additional suggestions")
    
    class Config:
        json_schema_extra = {
            "example": {
                "mode": "testing",
                "result": {
                    "type": "code",
                    "content": "import pytest\n\ndef test_example():\n    pass",
                    "metadata": {
                        "language": "python",
                        "test_framework": "pytest"
                    }
                },
                "suggestions": ["Add edge case tests", "Mock external APIs"]
            }
        }


class FileResponse(BaseModel):
    """Response schema for file information"""
    
    path: str = Field(..., description="File path")
    language: Optional[str] = Field(None, description="Programming language")
    lines: Optional[int] = Field(None, description="Number of lines")
    indexed: bool = Field(..., description="Whether file is indexed")


class WorkspaceResponse(BaseModel):
    """Response schema for workspace information"""
    
    workspace_id: str = Field(..., description="Workspace ID")
    type: str = Field(..., description="Workspace type")
    metadata: Dict[str, Any] = Field(..., description="Workspace metadata")
    created_at: datetime = Field(..., description="Creation timestamp")
    last_accessed: datetime = Field(..., description="Last access timestamp")
    file_count: Optional[int] = Field(None, description="Number of files")

# Made with Bob

"""Response schemas"""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime


class MessageResponse(BaseModel):
    """Response schema for a message"""
    
    id: str = Field(..., description="Message ID")
    conversation_id: str = Field(..., description="Conversation ID")
    role: str = Field(..., description="Message role")
    content: str = Field(..., description="Message content")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Message metadata")
    timestamp: datetime = Field(..., description="Message timestamp")
    
    class Config:
        from_attributes = True


class ConversationResponse(BaseModel):
    """Response schema for a conversation"""
    
    id: str = Field(..., description="Conversation ID")
    workspace_id: str = Field(..., description="Workspace ID")
    title: Optional[str] = Field(None, description="Conversation title")
    created_at: datetime = Field(..., description="Creation timestamp")
    last_updated: datetime = Field(..., description="Last update timestamp")
    message_count: int = Field(..., description="Number of messages")
    messages: List[MessageResponse] = Field(default_factory=list, description="Conversation messages")
    
    class Config:
        from_attributes = True

