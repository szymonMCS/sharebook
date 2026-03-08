"""Interfaces for book discovery services."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Optional


@dataclass
class BookSearchResult:
    """Result of a book search."""
    success: bool
    data: dict[str, Any] | None = None
    results: list[dict[str, Any]] | None = None
    source: str = ""
    confidence: float = 0.0
    error: str | None = None


@dataclass
class SearchQuery:
    """Normalized search query."""
    original: str
    cleaned: str
    is_isbn: bool
    normalized_isbn: Optional[str] = None


class IBookDiscoveryService(ABC):
    """Interface for book discovery/search services.
    
    Unified interface for searching books by ISBN or title using
    external APIs and AI-powered search.
    """
    
    @abstractmethod
    async def search_by_isbn(self, isbn: str) -> BookSearchResult:
        """Search book by ISBN.
        
        Args:
            isbn: ISBN-10 or ISBN-13
            
        Returns:
            BookSearchResult with book data
        """
        pass
    
    @abstractmethod
    async def search_by_title(self, title: str, author: Optional[str] = None) -> BookSearchResult:
        """Search books by title.
        
        Args:
            title: Book title
            author: Optional author name
            
        Returns:
            BookSearchResult with book data
        """
        pass
    
    @abstractmethod
    async def close(self) -> None:
        """Cleanup resources."""
        pass


class IQueryBuilder(ABC):
    """Interface for query builder."""
    
    @abstractmethod
    def normalize_isbn(self, isbn: str) -> str:
        """Remove dashes and spaces from ISBN."""
        pass
    
    @abstractmethod
    def is_isbn(self, query: str) -> bool:
        """Check if query is ISBN (10 or 13 digits)."""
        pass
    
    @abstractmethod
    def build(self, query: str) -> Optional[SearchQuery]:
        """Build a validated search query."""
        pass


class ISearchExecutor(ABC):
    """Interface for search executor."""
    
    @abstractmethod
    async def get_cover_from_openlibrary(self, isbn: str) -> Any:
        """Fetch cover URL from Open Library."""
        pass
    
    @abstractmethod
    async def get_cover_from_google(self, isbn: str) -> Any:
        """Fetch cover URL from Google Books."""
        pass
    
    @abstractmethod
    async def find_cover(self, isbn: str) -> Any:
        """Find cover from any available source."""
        pass
