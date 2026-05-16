"""Conversation management routes"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from app.database.session import get_db
from app.database.models import Conversation, Message, Workspace
from app.api.schemas.requests import MessageCreate
from app.api.schemas.responses import ConversationResponse, MessageResponse

router = APIRouter(tags=["conversations"])


@router.post("", response_model=ConversationResponse)
async def create_conversation(
    workspace_id: str,
    title: str = None,
    db: Session = Depends(get_db)
):
    """Create a new conversation for a workspace"""
    
    # Verify workspace exists
    workspace = db.query(Workspace).filter(Workspace.id == workspace_id).first()
    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace not found")
    
    # Create conversation
    conversation = Conversation(
        workspace_id=workspace_id,
        title=title or f"Conversation {datetime.utcnow().strftime('%Y-%m-%d %H:%M')}"
    )
    
    db.add(conversation)
    db.commit()
    db.refresh(conversation)
    
    return ConversationResponse(
        id=conversation.id,
        workspace_id=conversation.workspace_id,
        title=conversation.title,
        created_at=conversation.created_at,
        last_updated=conversation.last_updated,
        message_count=0,
        messages=[]
    )


@router.get("/{conversation_id}", response_model=ConversationResponse)
async def get_conversation(
    conversation_id: str,
    db: Session = Depends(get_db)
):
    """Get a conversation with all its messages"""
    
    conversation = db.query(Conversation).filter(
        Conversation.id == conversation_id
    ).first()
    
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    # Get all messages
    messages = db.query(Message).filter(
        Message.conversation_id == conversation_id
    ).order_by(Message.timestamp).all()
    
    return ConversationResponse(
        id=conversation.id,
        workspace_id=conversation.workspace_id,
        title=conversation.title,
        created_at=conversation.created_at,
        last_updated=conversation.last_updated,
        message_count=len(messages),
        messages=[
            MessageResponse(
                id=msg.id,
                conversation_id=msg.conversation_id,
                role=msg.role,
                content=msg.content,
                metadata=msg.message_metadata,
                timestamp=msg.timestamp
            )
            for msg in messages
        ]
    )


@router.post("/{conversation_id}/messages", response_model=MessageResponse)
async def add_message(
    conversation_id: str,
    message: MessageCreate,
    db: Session = Depends(get_db)
):
    """Add a message to a conversation"""
    
    # Verify conversation exists
    conversation = db.query(Conversation).filter(
        Conversation.id == conversation_id
    ).first()
    
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    # Create message
    new_message = Message(
        conversation_id=conversation_id,
        role=message.role,
        content=message.content,
        message_metadata=message.metadata
    )
    
    db.add(new_message)
    
    # Update conversation last_updated
    conversation.last_updated = datetime.utcnow()
    
    db.commit()
    db.refresh(new_message)
    
    return MessageResponse(
        id=new_message.id,
        conversation_id=new_message.conversation_id,
        role=new_message.role,
        content=new_message.content,
        metadata=new_message.message_metadata,
        timestamp=new_message.timestamp
    )


@router.get("/workspace/{workspace_id}", response_model=List[ConversationResponse])
async def list_conversations(
    workspace_id: str,
    db: Session = Depends(get_db)
):
    """List all conversations for a workspace"""
    
    # Verify workspace exists
    workspace = db.query(Workspace).filter(Workspace.id == workspace_id).first()
    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace not found")
    
    # Get all conversations
    conversations = db.query(Conversation).filter(
        Conversation.workspace_id == workspace_id
    ).order_by(Conversation.last_updated.desc()).all()
    
    result = []
    for conv in conversations:
        # Get message count
        message_count = db.query(Message).filter(
            Message.conversation_id == conv.id
        ).count()
        
        # Get recent messages (last 5)
        recent_messages = db.query(Message).filter(
            Message.conversation_id == conv.id
        ).order_by(Message.timestamp.desc()).limit(5).all()
        
        result.append(ConversationResponse(
            id=conv.id,
            workspace_id=conv.workspace_id,
            title=conv.title,
            created_at=conv.created_at,
            last_updated=conv.last_updated,
            message_count=message_count,
            messages=[
                MessageResponse(
                    id=msg.id,
                    conversation_id=msg.conversation_id,
                    role=msg.role,
                    content=msg.content,
                    metadata=msg.message_metadata,
                    timestamp=msg.timestamp
                )
                for msg in reversed(recent_messages)
            ]
        ))
    
    return result


@router.delete("/{conversation_id}")
async def delete_conversation(
    conversation_id: str,
    db: Session = Depends(get_db)
):
    """Delete a conversation and all its messages"""
    
    conversation = db.query(Conversation).filter(
        Conversation.id == conversation_id
    ).first()
    
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    db.delete(conversation)
    db.commit()
    
    return {"status": "success", "message": "Conversation deleted"}


@router.patch("/{conversation_id}/title")
async def update_conversation_title(
    conversation_id: str,
    title: str,
    db: Session = Depends(get_db)
):
    """Update conversation title"""
    
    conversation = db.query(Conversation).filter(
        Conversation.id == conversation_id
    ).first()
    
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    conversation.title = title
    conversation.last_updated = datetime.utcnow()
    
    db.commit()
    
    return {"status": "success", "title": title}

# Made with Bob
