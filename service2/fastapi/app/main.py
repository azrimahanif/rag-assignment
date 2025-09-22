"""
FastAPI application for RAG system
"""

import logging
import time
from contextlib import asynccontextmanager
from typing import Dict, Any

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
import structlog

from app.api import rag, health, monitoring
from app.routers import chat, webhook
from app.core.config import settings
from app.core.logging import setup_logging
from app.core.database import create_tables, close_db_connections
from app.services.qdrant_service import QdrantService
from app.services.openai_service import OpenAIService
from app.services.opik_service import get_opik_service

# Setup structured logging
setup_logging()
logger = structlog.get_logger()

# Prometheus metrics
REQUEST_COUNT = Counter('http_requests_total', 'Total HTTP requests', ['method', 'endpoint', 'status_code'])
REQUEST_DURATION = Histogram('http_request_duration_seconds', 'HTTP request duration')
ACTIVE_REQUESTS = Gauge('http_active_requests', 'Number of active HTTP requests')
RAG_ACCURACY = Gauge('rag_accuracy_score', 'RAG system accuracy score')
RAG_LATENCY = Histogram('rag_query_latency_seconds', 'RAG query latency')
RETRIEVAL_HIT_RATE = Gauge('rag_retrieval_hit_rate', 'RAG retrieval hit rate')

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    logger.info("Starting RAG FastAPI application")

    # Initialize services
    app.state.qdrant_service = QdrantService()
    app.state.openai_service = OpenAIService()
    app.state.opik_service = get_opik_service()

    # Create database tables
    try:
        await create_tables()
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error("Failed to create database tables", error=str(e))

    # Health check
    try:
        await app.state.qdrant_service.health_check()
        logger.info("Qdrant service connection established")
    except Exception as e:
        logger.error("Failed to connect to Qdrant service", error=str(e))

    # Opik health check
    try:
        if app.state.opik_service.is_enabled():
            logger.info("Opik service initialized successfully",
                       project_name=settings.OPIK_PROJECT_NAME,
                       enabled=settings.OPIK_ENABLED)
        else:
            logger.info("Opik service disabled or unavailable")
    except Exception as e:
        logger.error("Failed to initialize Opik service", error=str(e))

    yield

    # Cleanup
    logger.info("Shutting down RAG FastAPI application")
    await close_db_connections()

# Create FastAPI app
app = FastAPI(
    title="RAG System API",
    description="Retrieval-Augmented Generation system for population data",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_HOSTS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add metrics middleware
@app.middleware("http")
async def metrics_middleware(request, call_next):
    ACTIVE_REQUESTS.inc()
    start_time = time.time()
    
    try:
        response = await call_next(request)
        status_code = response.status_code
    except Exception as e:
        status_code = 500
        response = JSONResponse(
            status_code=status_code,
            content={"detail": str(e)}
        )
    
    # Record metrics
    REQUEST_COUNT.labels(
        method=request.method,
        endpoint=request.url.path,
        status_code=status_code
    ).inc()
    
    REQUEST_DURATION.observe(time.time() - start_time)
    ACTIVE_REQUESTS.dec()
    
    return response

# Include routers
app.include_router(health.router, prefix="/health", tags=["health"])
app.include_router(rag.router, prefix="/api/v1/rag", tags=["rag"])
app.include_router(monitoring.router, prefix="/api/v1/monitoring", tags=["monitoring"])
app.include_router(chat.router, prefix="/api/v1", tags=["chat"])
app.include_router(webhook.router, prefix="/api/v1", tags=["webhook"])

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "RAG System API",
        "version": "1.0.0",
        "docs": "/docs",
        "status": "operational"
    }

@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint"""
    return generate_latest()

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler"""
    logger.error("Unhandled exception", error=str(exc), path=request.url.path)
    
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
            "request_id": getattr(request.state, 'request_id', 'unknown')
        }
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower()
    )