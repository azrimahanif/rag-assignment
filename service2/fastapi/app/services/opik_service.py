"""
Opik service for LLM tracing and evaluation
"""

import os
from typing import Optional, Dict, Any, Union
import traceback

def _check_opik_availability():
    """Check if Opik is available dynamically"""
    try:
        import opik
        from opik import track
        from opik.opik_context import get_current_span
        return True, opik, track, get_current_span
    except ImportError:
        return False, None, None, None

# Check availability and set up modules
_OPIK_AVAILABLE, opik, track, get_current_span = _check_opik_availability()

# Create no-op decorator if Opik is not available
if not _OPIK_AVAILABLE:
    def track(name=None, project_name=None, **kwargs):
        def decorator(func):
            return func
        return decorator

    class DummyOpikContext:
        def get_current_span(self):
            return None

    def get_current_span():
        return None

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class OpikService:
    """Service for managing Opik LLM tracing and evaluation"""

    def __init__(self):
        # Check availability dynamically each time
        self._opik_available, self._opik, self._track, self._get_current_span = _check_opik_availability()
        self.enabled = settings.OPIK_ENABLED and self._opik_available
        self._initialized = False

        if self.enabled:
            self._initialize_opik()
        else:
            logger.warning(
                "Opik disabled - OPIK_ENABLED=%s, OPIK_AVAILABLE=%s",
                settings.OPIK_ENABLED,
                self._opik_available
            )

    def _initialize_opik(self):
        """Initialize Opik client"""
        try:
            # Configure Opik
            opik_config = settings.opik_config

            # Remove None values
            opik_config = {k: v for k, v in opik_config.items() if v is not None}

            # Initialize Opik
            self._opik.configure(**opik_config)

            self._initialized = True
            logger.info(
                "Opik initialized successfully",
                project_name=settings.OPIK_PROJECT_NAME,
                url=settings.OPIK_URL
            )

        except Exception as e:
            logger.error("Failed to initialize Opik", error=str(e))
            self.enabled = False
            self._initialized = False

    def is_enabled(self) -> bool:
        """Check if Opik is enabled and available"""
        return self.enabled and self._initialized

    def get_track_decorator(self, name: Optional[str] = None, **kwargs):
        """Get the track decorator with configuration"""
        if not self.is_enabled():
            # Return no-op decorator
            def decorator(func):
                return func
            return decorator

        # Configure decorator with project name
        track_kwargs = {"project_name": settings.OPIK_PROJECT_NAME}
        if name:
            track_kwargs["name"] = name
        track_kwargs.update(kwargs)

        return self._track(**track_kwargs)

    def log_metadata(self, metadata: Dict[str, Any]):
        """Log metadata to current span if available"""
        if not self.is_enabled():
            return

        try:
            current_span = self._get_current_span()
            if current_span:
                current_span.update_metadata(metadata)
        except Exception as e:
            logger.debug("Failed to log metadata to Opik", error=str(e))

    def log_feedback(self, feedback: Dict[str, Any]):
        """Log feedback to current span if available"""
        if not self.is_enabled():
            return

        try:
            current_span = self._get_current_span()
            if current_span:
                current_span.add_feedback(feedback)
        except Exception as e:
            logger.debug("Failed to log feedback to Opik", error=str(e))

    def create_span(self, name: str, metadata: Optional[Dict[str, Any]] = None):
        """Create a new span manually"""
        if not self.is_enabled():
            return None

        try:
            return self._opik.trace(name=name, metadata=metadata or {})
        except Exception as e:
            logger.debug("Failed to create Opik span", error=str(e))
            return None

    def end_span(self, span):
        """End a span"""
        if not self.is_enabled() or span is None:
            return

        try:
            span.end()
        except Exception as e:
            logger.debug("Failed to end Opik span", error=str(e))


# Global Opik service instance
opik_service = OpikService()


# Convenience functions
def track_llm_call(name: Optional[str] = None, **kwargs):
    """Decorator for tracking LLM calls"""
    return opik_service.get_track_decorator(name, **kwargs)


def log_llm_metadata(metadata: Dict[str, Any]):
    """Log metadata for current LLM call"""
    opik_service.log_metadata(metadata)


def log_llm_feedback(feedback: Dict[str, Any]):
    """Log feedback for current LLM call"""
    opik_service.log_feedback(feedback)


def get_opik_service() -> OpikService:
    """Get the Opik service instance"""
    return opik_service