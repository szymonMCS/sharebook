"""Cover service interfaces - simplified version."""
from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass
class SimpleCoverResult:
    """Result of cover operation."""
    isbn: str
    success: bool
    local_path: Optional[Path] = None
    error: Optional[str] = None
    from_cache: bool = False
    ai_generated: bool = False
    source: str = "none"

    @property
    def local_url(self) -> Optional[str]:
        return f"/covers/{self.isbn}.jpg" if self.local_path else None

    @property
    def openlibrary_url(self) -> str:
        return f"https://covers.openlibrary.org/b/isbn/{self.isbn}-M.jpg"


class ICoverService(ABC):
    """Interface for cover service (ShareBookCoverService).
    
    Flow: Cache -> OpenLibrary -> AI Fallback
    """
    
    @abstractmethod
    def exists_locally(self, isbn: str) -> bool:
        """Check if cover exists in local storage."""
        pass
    
    @abstractmethod
    def get_cover_url(self, isbn: str) -> Optional[str]:
        """Get the URL path for a cover if it exists locally."""
        pass
    
    @abstractmethod
    async def fetch_cover(
        self, 
        isbn: str, 
        book_title: Optional[str] = None,
        book_author: Optional[str] = None, 
        book_genre: Optional[str] = None,
        force_refresh: bool = False, 
        allow_ai_fallback: bool = True
    ) -> SimpleCoverResult:
        """Fetch cover from cache, OpenLibrary, or generate via AI."""
        pass
    
    @abstractmethod
    async def batch_fetch(self, books: list[dict], skip_existing: bool = True) -> list[SimpleCoverResult]:
        """Fetch covers for multiple books concurrently."""
        pass
    
    @abstractmethod
    async def close(self) -> None:
        """Close resources."""
        pass
