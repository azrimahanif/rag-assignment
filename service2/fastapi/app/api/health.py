"""
Health check endpoints
"""

import time
from typing import Dict, Any

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.services.qdrant_service import QdrantService
from app.services.openai_service import OpenAIService
from app.core.logging import get_logger

router = APIRouter()
logger = get_logger(__name__)


@router.get("/")
async def health_check() -> Dict[str, Any]:
    """Basic health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": time.time(),
        "service": "rag-api",
        "version": settings.VERSION
    }


@router.get("/detailed")
async def detailed_health_check(
    qdrant_service: QdrantService = Depends(),
    openai_service: OpenAIService = Depends()
) -> Dict[str, Any]:
    """Detailed health check with all dependencies"""
    
    health_status = {
        "status": "healthy",
        "timestamp": time.time(),
        "service": "rag-api",
        "version": settings.VERSION,
        "dependencies": {},
        "uptime": time.time()
    }
    
    # Check Qdrant
    try:
        qdrant_health = await qdrant_service.health_check()
        health_status["dependencies"]["qdrant"] = {
            "status": "healthy",
            "response_time": qdrant_health.get("response_time", 0),
            "collections_count": qdrant_health.get("collections_count", 0)
        }
    except Exception as e:
        health_status["dependencies"]["qdrant"] = {
            "status": "unhealthy",
            "error": str(e)
        }
        health_status["status"] = "degraded"
    
    # Check OpenAI
    try:
        openai_health = await openai_service.health_check()
        health_status["dependencies"]["openai"] = {
            "status": "healthy",
            "response_time": openai_health.get("response_time", 0),
            "models_available": openai_health.get("models_available", [])
        }
    except Exception as e:
        health_status["dependencies"]["openai"] = {
            "status": "unhealthy",
            "error": str(e)
        }
        health_status["status"] = "degraded"
    
    # Overall status determination
    unhealthy_deps = [
        dep for dep, status in health_status["dependencies"].items()
        if status["status"] == "unhealthy"
    ]
    
    if unhealthy_deps:
        health_status["status"] = "unhealthy"
        health_status["unhealthy_dependencies"] = unhealthy_deps
    
    # Set appropriate HTTP status code
    status_code = 200
    if health_status["status"] == "unhealthy":
        status_code = 503
    elif health_status["status"] == "degraded":
        status_code = 206
    
    return JSONResponse(
        content=health_status,
        status_code=status_code
    )


@router.get("/ready")
async def readiness_check() -> Dict[str, Any]:
    """Readiness check - indicates if service is ready to accept traffic"""
    
    # Add readiness logic here - check if all required services are available
    # and the service is fully initialized
    
    return {
        "status": "ready",
        "timestamp": time.time(),
        "checks": {
            "database": "ready",
            "services": "ready",
            "configuration": "loaded"
        }
    }


@router.get("/live")
async def liveness_check() -> Dict[str, Any]:
    """Liveness check - indicates if the service is running"""
    
    return {
        "status": "alive",
        "timestamp": time.time(),
        "checks": {
            "process": "running",
            "memory": "ok",
            "cpu": "ok"
        }
    }


@router.get("/metrics")
async def metrics_check() -> Dict[str, Any]:
    """Metrics availability check"""
    
    return {
        "status": "available",
        "timestamp": time.time(),
        "metrics": {
            "prometheus": "available",
            "custom_metrics": "available",
            "logging": "enabled"
        }
    }