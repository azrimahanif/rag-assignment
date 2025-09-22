"""
Webhook endpoints for n8n integration with chat storage
"""

from typing import Dict, Any, Optional
from fastapi import APIRouter, Request, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
import json
import time
from datetime import datetime

from app.core.database import get_db
from app.schemas.chat import ChatMessageCreate, ChatSessionCreate, ChatAnalyticsCreate
from app.services.chat_service import ChatService
from app.core.logger import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/webhook", tags=["webhook"])


@router.post("/chat-message")
async def webhook_chat_message(
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """
    Webhook endpoint to receive chat messages from n8n
    Expected payload:
    {
        "session_id": "unique_session_identifier",
        "message": "user message content",
        "response": "assistant response content",
        "metadata": {
            "query_type": "demographic_analysis",
            "response_time": 1500,
            "sources_used": ["malaysia_api", "state_parquet"],
            "additional_info": {}
        }
    }
    """
    try:
        # Parse request body
        body = await request.json()

        # Extract required fields
        session_id = body.get("session_id")
        user_message = body.get("message")
        assistant_response = body.get("response")
        metadata = body.get("metadata", {})

        if not session_id or not user_message or not assistant_response:
            raise HTTPException(
                status_code=400,
                detail="Missing required fields: session_id, message, response"
            )

        chat_service = ChatService(db)

        # Create session if it doesn't exist
        session_data = ChatSessionCreate(
            session_id=session_id,
            title=user_message[:50] + "..." if len(user_message) > 50 else user_message
        )
        await chat_service.create_session(session_data)

        # Store user message
        user_message_data = ChatMessageCreate(
            session_id=session_id,
            role="user",
            content=user_message,
            message_type="text",
            metadata={
                "timestamp": datetime.utcnow().isoformat(),
                "source": "n8n_webhook"
            }
        )
        await chat_service.add_message(user_message_data)

        # Store assistant response
        assistant_message_data = ChatMessageCreate(
            session_id=session_id,
            role="assistant",
            content=assistant_response,
            message_type="text",
            metadata={
                "timestamp": datetime.utcnow().isoformat(),
                "response_time_ms": metadata.get("response_time"),
                "sources_used": metadata.get("sources_used", []),
                "query_type": metadata.get("query_type"),
                "source": "n8n_webhook"
            }
        )
        await chat_service.add_message(assistant_message_data)

        # Store analytics if available
        if metadata.get("response_time") or metadata.get("query_type"):
            analytics_data = ChatAnalyticsCreate(
                session_id=session_id,
                query_type=metadata.get("query_type"),
                response_time=metadata.get("response_time"),
                message_count=2,  # user + assistant
                sources_used=metadata.get("sources_used", [])
            )
            await chat_service.add_analytics(analytics_data)

        logger.info(f"Stored chat messages for session {session_id}")

        return {
            "status": "success",
            "session_id": session_id,
            "message": "Chat messages stored successfully"
        }

    except HTTPException:
        raise
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON payload")
    except Exception as e:
        logger.error(f"Error processing webhook: {e}")
        raise HTTPException(status_code=500, detail="Failed to process webhook")


@router.post("/chat-start")
async def webhook_chat_start(
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """
    Webhook endpoint to initialize a new chat session
    Expected payload:
    {
        "session_id": "unique_session_identifier",
        "user_id": "optional_user_identifier",
        "initial_query": "What is Malaysia's population?"
    }
    """
    try:
        body = await request.json()

        session_id = body.get("session_id")
        user_id = body.get("user_id")
        initial_query = body.get("initial_query")

        if not session_id:
            raise HTTPException(
                status_code=400,
                detail="Missing required field: session_id"
            )

        chat_service = ChatService(db)

        # Create session
        session_data = ChatSessionCreate(
            session_id=session_id,
            user_id=user_id,
            title=f"Chat: {initial_query[:40]}..." if initial_query else "New Chat"
        )
        session = await chat_service.create_session(session_data)

        # Store initial query if provided
        if initial_query:
            message_data = ChatMessageCreate(
                session_id=session_id,
                role="user",
                content=initial_query,
                message_type="text",
                metadata={
                    "timestamp": datetime.utcnow().isoformat(),
                    "source": "n8n_webhook_start"
                }
            )
            await chat_service.add_message(message_data)

        logger.info(f"Initialized chat session {session_id}")

        return {
            "status": "success",
            "session_id": session_id,
            "message": "Chat session initialized successfully"
        }

    except HTTPException:
        raise
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON payload")
    except Exception as e:
        logger.error(f"Error initializing chat session: {e}")
        raise HTTPException(status_code=500, detail="Failed to initialize chat session")


@router.post("/analytics")
async def webhook_analytics(
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """
    Webhook endpoint to store analytics data
    Expected payload:
    {
        "session_id": "unique_session_identifier",
        "query_type": "demographic_analysis",
        "response_time": 1500,
        "message_count": 2,
        "sources_used": ["malaysia_api", "state_parquet"]
    }
    """
    try:
        body = await request.json()

        analytics_data = ChatAnalyticsCreate(
            session_id=body.get("session_id"),
            query_type=body.get("query_type"),
            response_time=body.get("response_time"),
            message_count=body.get("message_count", 1),
            sources_used=body.get("sources_used", [])
        )

        chat_service = ChatService(db)
        analytics = await chat_service.add_analytics(analytics_data)

        logger.info(f"Stored analytics for session {analytics_data.session_id}")

        return {
            "status": "success",
            "analytics_id": analytics.id,
            "message": "Analytics stored successfully"
        }

    except Exception as e:
        logger.error(f"Error storing analytics: {e}")
        raise HTTPException(status_code=500, detail="Failed to store analytics")


@router.get("/health")
async def webhook_health_check():
    """Health check for webhook endpoints"""
    return {"status": "healthy", "service": "webhook"}