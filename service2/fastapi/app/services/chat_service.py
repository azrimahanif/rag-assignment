"""
Chat service for managing chat history and sessions
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, func, and_
from sqlalchemy.orm import selectinload

from app.models.chat import ChatSession, ChatMessage, ChatAnalytics
from app.schemas.chat import (
    ChatMessageCreate, ChatSessionCreate, ChatAnalyticsCreate,
    ChatMessageResponse, ChatSessionResponse, ChatAnalyticsResponse
)
from app.core.logger import get_logger

logger = get_logger(__name__)


class ChatService:
    """Service for managing chat history and sessions"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_session(
        self,
        session_data: ChatSessionCreate
    ) -> ChatSessionResponse:
        """Create a new chat session"""
        try:
            # Check if session already exists
            existing_session = await self.get_session_by_id(session_data.session_id)
            if existing_session:
                return existing_session

            # Create new session
            session = ChatSession(
                session_id=session_data.session_id,
                user_id=session_data.user_id,
                title=session_data.title
            )

            self.db.add(session)
            await self.db.commit()
            await self.db.refresh(session)

            logger.info(f"Created new chat session: {session_data.session_id}")

            # Return response with message count (0 for new session)
            return ChatSessionResponse(
                id=session.id,
                session_id=session.session_id,
                user_id=session.user_id,
                title=session.title,
                created_at=session.created_at,
                updated_at=session.updated_at,
                is_active=session.is_active,
                message_count=0
            )

        except Exception as e:
            logger.error(f"Error creating chat session: {e}")
            await self.db.rollback()
            raise

    async def get_session_by_id(self, session_id: str) -> Optional[ChatSessionResponse]:
        """Get chat session by session_id"""
        try:
            result = await self.db.execute(
                select(ChatSession).where(ChatSession.session_id == session_id)
            )
            session = result.scalar_one_or_none()

            if session:
                # Get message count for this session
                count_result = await self.db.execute(
                    select(func.count(ChatMessage.id))
                    .where(ChatMessage.session_id == session_id)
                )
                message_count = count_result.scalar() or 0

                # Create response with message count
                session_response = ChatSessionResponse(
                    id=session.id,
                    session_id=session.session_id,
                    user_id=session.user_id,
                    title=session.title,
                    created_at=session.created_at,
                    updated_at=session.updated_at,
                    is_active=session.is_active,
                    message_count=message_count
                )
                return session_response
            return None

        except Exception as e:
            logger.error(f"Error getting session {session_id}: {e}")
            return None

    async def add_message(
        self,
        message_data: ChatMessageCreate
    ) -> ChatMessageResponse:
        """Add a message to chat history"""
        try:
            # Ensure session exists
            session = await self.get_session_by_id(message_data.session_id)
            if not session:
                # Create session if it doesn't exist
                session_data = ChatSessionCreate(session_id=message_data.session_id)
                await self.create_session(session_data)

            # Create message with proper metadata handling
            metadata = message_data.message_metadata or {}
            if metadata:
                # Ensure metadata is JSON serializable
                try:
                    # Test if metadata is serializable
                    import json
                    json.dumps(metadata)
                except (TypeError, ValueError) as json_error:
                    logger.warning(f"Metadata not serializable, using empty metadata: {json_error}")
                    metadata = {}

            message = ChatMessage(
                session_id=message_data.session_id,
                role=message_data.role,
                content=message_data.content,
                message_type=message_data.message_type or "text",
                metadata=metadata
            )

            self.db.add(message)

            # Update session updated_at timestamp
            await self.db.execute(
                select(ChatSession)
                .where(ChatSession.session_id == message_data.session_id)
                .execution_options(synchronize_session="fetch")
            )

            await self.db.commit()
            await self.db.refresh(message)

            logger.debug(f"Added message to session {message_data.session_id}: {message_data.role}")
            return ChatMessageResponse.model_validate(message)

        except Exception as e:
            logger.error(f"Error adding message: {e}")
            await self.db.rollback()
            raise

    async def get_session_messages(
        self,
        session_id: str,
        limit: int = 50,
        offset: int = 0
    ) -> List[ChatMessageResponse]:
        """Get messages for a session"""
        try:
            result = await self.db.execute(
                select(ChatMessage)
                .where(ChatMessage.session_id == session_id)
                .order_by(ChatMessage.created_at.desc())
                .offset(offset)
                .limit(limit)
            )

            messages = result.scalars().all()
            return [ChatMessageResponse.model_validate(msg) for msg in messages]

        except Exception as e:
            logger.error(f"Error getting messages for session {session_id}: {e}")
            return []

    async def get_session_with_messages(
        self,
        session_id: str,
        limit: int = 50
    ) -> Optional[Dict[str, Any]]:
        """Get session with all messages"""
        try:
            # Get session
            session_result = await self.db.execute(
                select(ChatSession)
                .options(selectinload(ChatSession.messages))
                .where(ChatSession.session_id == session_id)
            )

            session = session_result.scalar_one_or_none()
            if not session:
                return None

            # Get messages (limited)
            messages_result = await self.db.execute(
                select(ChatMessage)
                .where(ChatMessage.session_id == session_id)
                .order_by(ChatMessage.created_at.desc())
                .limit(limit)
            )

            messages = messages_result.scalars().all()

            return {
                "session": ChatSessionResponse.from_orm(session),
                "messages": [ChatMessageResponse.from_orm(msg) for msg in messages]
            }

        except Exception as e:
            logger.error(f"Error getting session with messages: {e}")
            return None

    async def list_sessions(
        self,
        user_id: Optional[str] = None,
        limit: int = 20,
        offset: int = 0
    ) -> Dict[str, Any]:
        """List chat sessions"""
        try:
            # Build query
            query = select(ChatSession)
            if user_id:
                query = query.where(ChatSession.user_id == user_id)

            # Get total count
            count_result = await self.db.execute(
                select(func.count(ChatSession.id)).where(
                    *([ChatSession.user_id == user_id] if user_id else [])
                )
            )
            total = count_result.scalar()

            # Get sessions
            result = await self.db.execute(
                query
                .order_by(ChatSession.updated_at.desc())
                .offset(offset)
                .limit(limit)
            )

            sessions = result.scalars().all()

            # Calculate message counts for each session
            session_responses = []
            for session in sessions:
                count_result = await self.db.execute(
                    select(func.count(ChatMessage.id))
                    .where(ChatMessage.session_id == session.session_id)
                )
                message_count = count_result.scalar() or 0

                session_response = ChatSessionResponse(
                    id=session.id,
                    session_id=session.session_id,
                    user_id=session.user_id,
                    title=session.title,
                    created_at=session.created_at,
                    updated_at=session.updated_at,
                    is_active=session.is_active,
                    message_count=message_count
                )
                session_responses.append(session_response)

            return {
                "sessions": session_responses,
                "total": total,
                "page": offset // limit + 1,
                "per_page": limit
            }

        except Exception as e:
            logger.error(f"Error listing sessions: {e}")
            return {"sessions": [], "total": 0, "page": 1, "per_page": limit}

    async def delete_session(self, session_id: str) -> bool:
        """Delete a chat session and all its messages"""
        try:
            # Delete session (cascades to messages)
            result = await self.db.execute(
                delete(ChatSession).where(ChatSession.session_id == session_id)
            )

            await self.db.commit()
            deleted = result.rowcount > 0

            if deleted:
                logger.info(f"Deleted chat session: {session_id}")

            return deleted

        except Exception as e:
            logger.error(f"Error deleting session {session_id}: {e}")
            await self.db.rollback()
            return False

    async def add_analytics(
        self,
        analytics_data: ChatAnalyticsCreate
    ) -> ChatAnalyticsResponse:
        """Add chat analytics"""
        try:
            # Handle sources_used field properly
            sources_used = analytics_data.sources_used or []
            if sources_used:
                # Ensure sources_used is JSON serializable
                try:
                    import json
                    json.dumps(sources_used)
                except (TypeError, ValueError) as json_error:
                    logger.warning(f"Sources not serializable, using empty list: {json_error}")
                    sources_used = []

            analytics = ChatAnalytics(
                session_id=analytics_data.session_id,
                query_type=analytics_data.query_type,
                response_time=analytics_data.response_time,
                message_count=analytics_data.message_count,
                sources_used=sources_used
            )

            self.db.add(analytics)
            await self.db.commit()
            await self.db.refresh(analytics)

            return ChatAnalyticsResponse.model_validate(analytics)

        except Exception as e:
            logger.error(f"Error adding analytics: {e}")
            await self.db.rollback()
            raise

    async def get_session_analytics(
        self,
        session_id: str,
        limit: int = 100
    ) -> List[ChatAnalyticsResponse]:
        """Get analytics for a session"""
        try:
            result = await self.db.execute(
                select(ChatAnalytics)
                .where(ChatAnalytics.session_id == session_id)
                .order_by(ChatAnalytics.created_at.desc())
                .limit(limit)
            )

            analytics = result.scalars().all()
            return [ChatAnalyticsResponse.model_validate(analytic) for analytic in analytics]

        except Exception as e:
            logger.error(f"Error getting analytics for session {session_id}: {e}")
            return []