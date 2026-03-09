from .health import router as health_router
from .ai import router as ai_router
from .websocket import router as websocket_router

__all__ = ["health_router", "ai_router", "websocket_router"]
