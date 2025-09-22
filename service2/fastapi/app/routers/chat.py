"""
Chat API endpoints for managing chat history
"""

from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.chat import (
    ChatMessageCreate, ChatSessionCreate, ChatAnalyticsCreate,
    ChatMessageResponse, ChatSessionResponse, ChatAnalyticsResponse,
    ChatHistoryRequest, ChatListResponse
)
from app.services.chat_service import ChatService
from app.core.logger import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("/session", response_model=ChatSessionResponse)
async def create_chat_session(
    session_data: ChatSessionCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new chat session"""
    try:
        chat_service = ChatService(db)
        session = await chat_service.create_session(session_data)
        return session

    except Exception as e:
        logger.error(f"Error creating chat session: {e}")
        raise HTTPException(status_code=500, detail="Failed to create chat session")


@router.get("/session/{session_id}", response_model=ChatSessionResponse)
async def get_chat_session(
    session_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get chat session by ID"""
    try:
        chat_service = ChatService(db)
        session = await chat_service.get_session_by_id(session_id)

        if not session:
            raise HTTPException(status_code=404, detail="Chat session not found")

        return session

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting chat session: {e}")
        raise HTTPException(status_code=500, detail="Failed to get chat session")


@router.post("/message", response_model=ChatMessageResponse)
async def add_chat_message(
    message_data: ChatMessageCreate,
    db: AsyncSession = Depends(get_db)
):
    """Add a message to chat history"""
    try:
        chat_service = ChatService(db)
        message = await chat_service.add_message(message_data)
        return message

    except Exception as e:
        logger.error(f"Error adding chat message: {e}")
        raise HTTPException(status_code=500, detail="Failed to add chat message")


@router.get("/session/{session_id}/messages", response_model=List[ChatMessageResponse])
async def get_session_messages(
    session_id: str,
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    db: AsyncSession = Depends(get_db)
):
    """Get messages for a specific session"""
    try:
        chat_service = ChatService(db)
        messages = await chat_service.get_session_messages(session_id, limit, offset)
        return messages

    except Exception as e:
        logger.error(f"Error getting session messages: {e}")
        raise HTTPException(status_code=500, detail="Failed to get session messages")


@router.get("/session/{session_id}/full")
async def get_session_with_messages(
    session_id: str,
    limit: int = Query(default=50, ge=1, le=200),
    db: AsyncSession = Depends(get_db)
):
    """Get session with all messages"""
    try:
        chat_service = ChatService(db)
        result = await chat_service.get_session_with_messages(session_id, limit)

        if not result:
            raise HTTPException(status_code=404, detail="Chat session not found")

        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting session with messages: {e}")
        raise HTTPException(status_code=500, detail="Failed to get session with messages")


@router.get("/sessions", response_model=ChatListResponse)
async def list_chat_sessions(
    user_id: Optional[str] = Query(default=None),
    limit: int = Query(default=20, ge=1, le=100),
    page: int = Query(default=1, ge=1),
    db: AsyncSession = Depends(get_db)
):
    """List chat sessions with pagination"""
    try:
        chat_service = ChatService(db)
        offset = (page - 1) * limit
        result = await chat_service.list_sessions(user_id, limit, offset)
        return result

    except Exception as e:
        logger.error(f"Error listing chat sessions: {e}")
        raise HTTPException(status_code=500, detail="Failed to list chat sessions")


@router.delete("/session/{session_id}")
async def delete_chat_session(
    session_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Delete a chat session and all its messages"""
    try:
        chat_service = ChatService(db)
        deleted = await chat_service.delete_session(session_id)

        if not deleted:
            raise HTTPException(status_code=404, detail="Chat session not found")

        return {"message": "Chat session deleted successfully"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting chat session: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete chat session")


@router.post("/analytics", response_model=ChatAnalyticsResponse)
async def add_chat_analytics(
    analytics_data: ChatAnalyticsCreate,
    db: AsyncSession = Depends(get_db)
):
    """Add chat analytics data"""
    try:
        chat_service = ChatService(db)
        analytics = await chat_service.add_analytics(analytics_data)
        return analytics

    except Exception as e:
        logger.error(f"Error adding chat analytics: {e}")
        raise HTTPException(status_code=500, detail="Failed to add chat analytics")


@router.get("/session/{session_id}/analytics", response_model=List[ChatAnalyticsResponse])
async def get_session_analytics(
    session_id: str,
    limit: int = Query(default=100, ge=1, le=500),
    db: AsyncSession = Depends(get_db)
):
    """Get analytics for a specific session"""
    try:
        chat_service = ChatService(db)
        analytics = await chat_service.get_session_analytics(session_id, limit)
        return analytics

    except Exception as e:
        logger.error(f"Error getting session analytics: {e}")
        raise HTTPException(status_code=500, detail="Failed to get session analytics")


@router.get("/health")
async def chat_health_check():
    """Health check for chat endpoints"""
    return {"status": "healthy", "service": "chat"}