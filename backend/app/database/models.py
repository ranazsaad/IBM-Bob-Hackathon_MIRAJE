"""Database models"""

from sqlalchemy import Column, String, Integer, Text, Boolean, DateTime, JSON, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

Base = declarative_base()


def generate_uuid():
    """Generate UUID string"""
    return str(uuid.uuid4())


class Workspace(Base):
    """Workspace model for storing analyzed repositories or transcripts"""
    
    __tablename__ = "workspaces"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    type = Column(String, nullable=False)  # 'github' or 'transcript'
    workspace_metadata = Column("metadata", JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_accessed = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    files = relationship("File", back_populates="workspace", cascade="all, delete-orphan")
    queries = relationship("Query", back_populates="workspace", cascade="all, delete-orphan")
    conversations = relationship("Conversation", back_populates="workspace", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Workspace(id={self.id}, type={self.type})>"


class File(Base):
    """File model for storing indexed files from repositories"""
    
    __tablename__ = "files"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    workspace_id = Column(String, ForeignKey("workspaces.id"), nullable=False)
    file_path = Column(String, nullable=False)
    language = Column(String, nullable=True)
    content = Column(Text, nullable=True)
    lines = Column(Integer, nullable=True)
    indexed = Column(Boolean, default=False)
    
    # Relationships
    workspace = relationship("Workspace", back_populates="files")
    
    def __repr__(self):
        return f"<File(id={self.id}, path={self.file_path})>"


class Query(Base):
    """Query model for caching AI responses"""
    
    __tablename__ = "queries"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    workspace_id = Column(String, ForeignKey("workspaces.id"), nullable=False)
    mode = Column(String, nullable=False)
    query_text = Column(Text, nullable=False)
    response = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    workspace = relationship("Workspace", back_populates="queries")
    
    def __repr__(self):
        return f"<Query(id={self.id}, mode={self.mode})>"


class Conversation(Base):
    """Conversation model for storing chat history"""
    
    __tablename__ = "conversations"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    workspace_id = Column(String, ForeignKey("workspaces.id"), nullable=False)
    title = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    workspace = relationship("Workspace", back_populates="conversations")
    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Conversation(id={self.id}, workspace_id={self.workspace_id})>"


class Message(Base):
    """Message model for storing individual chat messages"""
    
    __tablename__ = "messages"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    conversation_id = Column(String, ForeignKey("conversations.id"), nullable=False)
    role = Column(String, nullable=False)  # 'user', 'assistant', 'system'
    content = Column(Text, nullable=False)
    message_metadata = Column("metadata", JSON, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    conversation = relationship("Conversation", back_populates="messages")
    
    def __repr__(self):
        return f"<Message(id={self.id}, role={self.role})>"


# Made with IBM watsonx.ai
