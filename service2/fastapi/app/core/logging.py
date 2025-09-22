"""
Logging configuration for the application
"""

import logging
import logging.handlers
import logging.config
import sys
import time
from typing import Any, Dict

import structlog
from pythonjsonlogger import jsonlogger

from app.core.config import settings


def setup_logging() -> None:
    """Setup structured logging for the application"""
    
    # Configure structlog
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.JSONRenderer()
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )
    
    # Configure standard logging
    logging_config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "json": {
                "()": jsonlogger.JsonFormatter,
                "fmt": "%(asctime)s %(name)s %(levelname)s %(message)s",
            },
            "standard": {
                "format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
            },
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "level": settings.LOG_LEVEL,
                "formatter": "json" if settings.LOG_FORMAT == "json" else "standard",
                "stream": sys.stdout,
            },
        },
        "loggers": {
            "": {
                "handlers": ["console"],
                "level": settings.LOG_LEVEL,
                "propagate": False,
            },
            "uvicorn": {
                "handlers": ["console"],
                "level": "INFO",
                "propagate": False,
            },
            "uvicorn.access": {
                "handlers": ["console"],
                "level": "INFO",
                "propagate": False,
            },
        },
    }
    
    logging.config.dictConfig(logging_config)
    
    # Set up structlog logger
    logger = structlog.get_logger()
    logger.info("Logging configured", level=settings.LOG_LEVEL, format=settings.LOG_FORMAT)


class RequestLoggingMiddleware:
    """Middleware for request logging"""
    
    def __init__(self, app):
        self.app = app
        self.logger = structlog.get_logger("request")
    
    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        
        # Extract request information
        method = scope["method"]
        path = scope["path"]
        query_string = scope.get("query_string", b"").decode()
        
        # Generate request ID
        import uuid
        request_id = str(uuid.uuid4())
        
        # Add request ID to scope
        scope["request_id"] = request_id
        
        # Log request start
        self.logger.info(
            "Request started",
            method=method,
            path=path,
            query_string=query_string,
            request_id=request_id,
        )
        
        start_time = time.time()
        
        async def send_wrapper(message):
            if message["type"] == "http.response.start":
                # Log request completion
                duration = time.time() - start_time
                status_code = message["status"]
                
                self.logger.info(
                    "Request completed",
                    method=method,
                    path=path,
                    status_code=status_code,
                    duration=duration,
                    request_id=request_id,
                )
            
            await send(message)
        
        await self.app(scope, receive, send_wrapper)


def get_logger(name: str) -> structlog.stdlib.BoundLogger:
    """Get a structured logger instance"""
    return structlog.get_logger(name)


def log_execution_time(logger: structlog.stdlib.BoundLogger, operation: str):
    """Decorator to log execution time"""
    def decorator(func):
        async def async_wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = await func(*args, **kwargs)
                duration = time.time() - start_time
                logger.info(
                    "Operation completed",
                    operation=operation,
                    duration=duration,
                    success=True,
                )
                return result
            except Exception as e:
                duration = time.time() - start_time
                logger.error(
                    "Operation failed",
                    operation=operation,
                    duration=duration,
                    success=False,
                    error=str(e),
                )
                raise
        
        def sync_wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                duration = time.time() - start_time
                logger.info(
                    "Operation completed",
                    operation=operation,
                    duration=duration,
                    success=True,
                )
                return result
            except Exception as e:
                duration = time.time() - start_time
                logger.error(
                    "Operation failed",
                    operation=operation,
                    duration=duration,
                    success=False,
                    error=str(e),
                )
                raise
        
        import asyncio
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator