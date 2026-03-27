import asyncio
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Literal
from src.config import settings
from src.services.interfaces.cover import ICoverService
from .downloader import CoverDownloader
from .simple_storage import SimpleCoverStorage
from .ai_generator import CoverAIGenerator

logger = logging.getLogger(__name__)

_init_lock: asyncio.Lock = asyncio.Lock()


@dataclass
class SimpleCoverResult:
    isbn: str
    success: bool
    local_path: Optional[Path] = None
    error: Optional[str] = None
    from_cache: bool = False
    ai_generated: bool = False
    source: Literal["openlibrary", "ai", "cache", "none"] = "none"

    @property
    def local_url(self) -> Optional[str]:
        return f"/covers/{self.isbn}.jpg" if self.local_path else None
    @property
    def openlibrary_url(self) -> str:
        return f"https://covers.openlibrary.org/b/isbn/{self.isbn}-M.jpg"


class ShareBookCoverService(ICoverService):
    def __init__(
        self,
        covers_dir: Optional[Path] = None,
        size: Literal["S", "M", "L"] = "M",
        max_concurrent: int = 5,
        delay_seconds: float = 0.2,
        ai_generator: Optional[CoverAIGenerator] = None,
        openai_api_key: Optional[str] = None
    ):
        self.storage = SimpleCoverStorage(covers_dir)
        self.downloader = CoverDownloader(timeout=15.0, size=size)
        self.size, self.max_concurrent, self.delay = size, max_concurrent, delay_seconds
        if ai_generator:
            self.ai_generator = ai_generator
        elif openai_api_key:
            self.ai_generator = CoverAIGenerator(openai_api_key=openai_api_key)
        else:
            self.ai_generator = CoverAIGenerator(use_dalle=False)

    def exists_locally(self, isbn: str) -> bool:
        return self.storage.exists(isbn)

    def get_cover_url(self, isbn: str) -> Optional[str]:
        return self.storage.get_url_path(isbn)

    async def fetch_cover(
        self, isbn: str, book_title: Optional[str] = None,
        book_author: Optional[str] = None, book_genre: Optional[str] = None,
        force_refresh: bool = False, allow_ai_fallback: bool = True
    ) -> SimpleCoverResult:
        clean_isbn = isbn.replace("-", "").replace(" ", "").strip()
        
        if not force_refresh and self.storage.exists(clean_isbn):
            return SimpleCoverResult(isbn=clean_isbn, success=True, local_path=self.storage.get_cover_path(clean_isbn), from_cache=True, source="cache")
        result = await self.downloader.download_from_openlibrary(clean_isbn)
        if result.success and result.data:
            cover_path = self.storage.save(clean_isbn, result.data)
            return SimpleCoverResult(isbn=clean_isbn, success=True, local_path=cover_path, source="openlibrary")
        if allow_ai_fallback and book_title:
            logger.info(f"Cover not in OL for {clean_isbn}, using AI...")
            return await self._generate_ai_cover(clean_isbn, book_title, book_author, book_genre)
        
        return SimpleCoverResult(isbn=clean_isbn, success=False, error=result.error or "Cover not found", source="none")

    async def _generate_ai_cover(self, isbn: str, title: str, author: Optional[str] = None, genre: Optional[str] = None) -> SimpleCoverResult:
        try:
            image_data = await self.ai_generator.generate_cover(title=title, author=author or "Unknown Author", isbn=isbn, genre=genre)
            if image_data:
                cover_path = self.storage.save(isbn, image_data)
                return SimpleCoverResult(isbn=isbn, success=True, local_path=cover_path, ai_generated=True, source="ai")
            return SimpleCoverResult(isbn=isbn, success=False, error="AI generation failed", source="none")
        except Exception as e:
            logger.error(f"AI generation error: {e}")
            return SimpleCoverResult(isbn=isbn, success=False, error=f"AI generation failed: {e}", source="none")

    async def batch_fetch(self, books: list[dict], skip_existing: bool = True) -> list[SimpleCoverResult]:
        semaphore = asyncio.Semaphore(self.max_concurrent)
        
        async def fetch_one(book: dict) -> SimpleCoverResult:
            async with semaphore:
                isbn = book['isbn'].replace("-", "").replace(" ", "").strip()
                if skip_existing and self.storage.exists(isbn):
                    return SimpleCoverResult(isbn=isbn, success=True, local_path=self.storage.get_cover_path(isbn), from_cache=True, source="cache")
                
                result = await self.fetch_cover(isbn=book['isbn'], book_title=book.get('title'), book_author=book.get('author'), book_genre=book.get('genre'))
                await asyncio.sleep(self.delay)
                return result
        return await asyncio.gather(*[fetch_one(book) for book in books])

    async def close(self) -> None:
        await self.downloader.close()
        await self.ai_generator.close()

_cover_service: Optional[ShareBookCoverService] = None

async def get_cover_service(openai_api_key: Optional[str] = None, use_ai: bool = False) -> ShareBookCoverService:
    global _cover_service
    if _cover_service is None:
        async with _init_lock:
            if _cover_service is None:
                _cover_service = ShareBookCoverService(openai_api_key=openai_api_key if use_ai else None)
    return _cover_service

def create_cover_service(
    covers_dir: Optional[Path] = None,
    size: Literal["S", "M", "L"] = "M",
    max_concurrent: int = 5,
    delay_seconds: float = 0.2,
    openai_api_key: Optional[str] = None,
    use_ai: bool = False
) -> ShareBookCoverService:
    api_key = openai_api_key if use_ai else None
    if use_ai and api_key is None:
        api_key = settings.OPENAI_API_KEY or None
    
    return ShareBookCoverService(
        covers_dir=covers_dir,
        size=size,
        max_concurrent=max_concurrent,
        delay_seconds=delay_seconds,
        openai_api_key=api_key
    )
