"""Workspace-related schemas"""

from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class FileMetadata(BaseModel):
    """File metadata schema"""
    
    path: str = Field(..., description="File path")
    language: Optional[str] = Field(None, description="Programming language")
    lines: int = Field(..., description="Number of lines")
    size: Optional[int] = Field(None, description="File size in bytes")


class WorkspaceMetadata(BaseModel):
    """Workspace metadata schema"""
    
    repo_name: Optional[str] = Field(None, description="Repository name")
    language: Optional[str] = Field(None, description="Primary language")
    file_count: int = Field(..., description="Number of files")
    total_lines: int = Field(..., description="Total lines of code")
    structure: Optional[dict] = Field(None, description="Directory structure")
    key_files: Optional[List[str]] = Field(None, description="Key files identified")


class UserStory(BaseModel):
    """User story schema"""
    
    title: str = Field(..., description="User story title")
    description: str = Field(..., description="User story description")
    acceptance_criteria: List[str] = Field(..., description="Acceptance criteria")
    priority: Optional[str] = Field("medium", description="Priority level")
    estimate: Optional[str] = Field(None, description="Time estimate")


class EngineeringTicket(BaseModel):
    """Engineering ticket schema"""
    
    type: str = Field(..., description="Ticket type: feature, bug, task")
    title: str = Field(..., description="Ticket title")
    description: str = Field(..., description="Ticket description")
    priority: str = Field(..., description="Priority: low, medium, high, critical")
    estimate: Optional[str] = Field(None, description="Time estimate")
    labels: Optional[List[str]] = Field(None, description="Ticket labels")
    dependencies: Optional[List[str]] = Field(None, description="Dependencies")

# Made with Bob
