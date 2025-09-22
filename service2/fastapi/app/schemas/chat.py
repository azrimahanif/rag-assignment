"""
Chat-related Pydantic schemas
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field


class ChatMessageCreate(BaseModel):
    """Schema for creating a chat message"""
    session_id: str = Field(..., description="Session identifier")
    role: str = Field(..., description="Message role (user/assistant)")
    content: str = Field(..., description="Message content")
    message_type: str = Field(default="text", description="Message type")
    message_metadata: Optional[Dict[str, Any]] = Field(default=None, description="Additional message data")


class ChatMessageResponse(BaseModel):
    """Schema for chat message response"""
    id: int
    session_id: str
    role: str
    content: str
    message_type: str
    message_metadata: Optional[Dict[str, Any]]
    created_at: datetime

    class Config:
        from_attributes = True


class ChatSessionCreate(BaseModel):
    """Schema for creating a chat session"""
    session_id: str = Field(..., description="Session identifier")
    user_id: Optional[str] = Field(default=None, description="User identifier")
    title: Optional[str] = Field(default=None, description="Session title")


class ChatSessionResponse(BaseModel):
    """Schema for chat session response"""
    id: int
    session_id: str
    user_id: Optional[str]
    title: Optional[str]
    created_at: datetime
    updated_at: datetime
    is_active: bool
    message_count: int = 0

    class Config:
        from_attributes = True


class ChatSessionWithMessages(BaseModel):
    """Schema for chat session with messages"""
    session: ChatSessionResponse
    messages: List[ChatMessageResponse]


class ChatAnalyticsCreate(BaseModel):
    """Schema for creating chat analytics"""
    session_id: Optional[str] = Field(default=None, description="Session identifier")
    query_type: Optional[str] = Field(default=None, description="Type of query")
    response_time: Optional[int] = Field(default=None, description="Response time in ms")
    message_count: int = Field(default=1, description="Number of messages")
    sources_used: Optional[List[str]] = Field(default=None, description="Data sources used")


class ChatAnalyticsResponse(BaseModel):
    """Schema for chat analytics response"""
    id: int
    session_id: Optional[str]
    query_type: Optional[str]
    response_time: Optional[int]
    message_count: int
    sources_used: Optional[List[str]]
    created_at: datetime

    class Config:
        from_attributes = True


class ChatHistoryRequest(BaseModel):
    """Schema for requesting chat history"""
    session_id: str = Field(..., description="Session identifier")
    limit: int = Field(default=50, description="Number of messages to retrieve")
    offset: int = Field(default=0, description="Offset for pagination")


class ChatListResponse(BaseModel):
    """Schema for listing chat sessions"""
    sessions: List[ChatSessionResponse]
    total: int
    page: int
    per_page: int