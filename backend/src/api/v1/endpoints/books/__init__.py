from .books import router as books_router
from .community import router as community_router
from .covers import router as covers_router

__all__ = ["books_router", "community_router", "covers_router"]
