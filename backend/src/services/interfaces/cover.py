from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import Optional
from enum import Enum


class CoverSourceType(Enum):
    OPENLIBRARY = "openlibrary"
    GOOGLE_BOOKS = "google_books"
    AI_GENERATED = "ai"
    CACHE = "cache"
    NONE = "none"


@dataclass
class CoverResult:
    isbn: str
    success: bool
    data: Optional[bytes] = None
    local_path: Optional[Path] = None
    error: Optional[str] = None
    source: CoverSourceType = CoverSourceType.NONE
    from_cache: bool = False
    ai_generated: bool = False

    @property
    def local_url(self) -> Optional[str]:
        return f"/covers/{self.isbn}.jpg" if self.local_path else None

    @property
    def openlibrary_url(self) -> str:
        return f"https://covers.openlibrary.org/b/isbn/{self.isbn}-M.jpg"


class ICoverSource(ABC):
    @property
    @abstractmethod
    def source_type(self) -> CoverSourceType:
        pass
    @abstractmethod
    async def fetch_cover(self, isbn: str, book_title: Optional[str] = None, book_author: Optional[str] = None, book_genre: Optional[str] = None) -> CoverResult:
        pass
    @abstractmethod
    def is_available(self) -> bool:
        pass
    @abstractmethod
    def get_priority(self) -> int:
        pass


class ISourceStrategy(ABC):
    @abstractmethod
    async def fetch_cover(
        self,
        sources: list[ICoverSource],
        isbn: str,
        book_title: Optional[str] = None,
        book_author: Optional[str] = None,
        book_genre: Optional[str] = None
    ) -> CoverResult:
        pass
