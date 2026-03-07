import asyncio
import logging
from pathlib import Path
from src.services.interfaces import ICoverSource, ISourceStrategy, CoverResult, CoverSourceType
from src.services.cover.storage import CoverStorage
from src.config import settings

logger = logging.getLogger(__name__)


class CoverManager:
    def __init__(
        self,
        sources: list[ICoverSource],
        strategy: ISourceStrategy,
        storage: CoverStorage | None = None,
        max_concurrent: int = 5,
        delay_seconds: float = 0.2
    ):
        self.sources = sources
        self.strategy = strategy
        self.storage = storage or CoverStorage(Path(settings.COVERS_PATH))
        self.max_concurrent = max_concurrent
        self.delay = delay_seconds
        self._locks: dict[str, asyncio.Lock] = {}
        self._global_lock = asyncio.Lock()
        self._processing: set[str] = set()
        self._processing_lock = asyncio.Lock()

    def exists(self, isbn: str) -> bool:
        return self.storage.exists(isbn)

    def get_url(self, isbn: str) -> str | None:
        return self.storage.get_url_path(isbn)

    async def _get_lock(self, isbn: str) -> asyncio.Lock:
        async with self._global_lock:
            if len(self._locks) >= 1000:
                keys = list(self._locks.keys())[:200]
                for k in keys:
                    del self._locks[k]

            if isbn not in self._locks:
                self._locks[isbn] = asyncio.Lock()
            return self._locks[isbn]

    async def fetch(self, isbn: str, book_title: str | None = None, book_author: str | None = None, book_genre: str | None = None, force_refresh: bool = False) -> CoverResult:
        clean_isbn = isbn.replace("-", "").replace(" ", "").strip()
        lock = await self._get_lock(clean_isbn)

        async with lock:
            if not force_refresh and self.storage.exists(clean_isbn):
                return CoverResult(
                    isbn=clean_isbn,
                    success=True,
                    local_path=self.storage.get_cover_path(clean_isbn),
                    from_cache=True,
                    source=CoverSourceType.CACHE
                )
            result = await self.strategy.fetch_cover(self.sources, clean_isbn, book_title, book_author, book_genre)

            if result.success and result.data:
                path = self.storage.save(clean_isbn, result.data)
                result.local_path = path

            return result

    async def batch_fetch(self, books: list[dict], skip_existing: bool = True) -> list[CoverResult]:
        async with self._processing_lock:
            unique = []
            seen = set()
            for b in books:
                isbn = b['isbn'].replace("-", "").replace(" ", "").strip()
                if isbn not in self._processing and isbn not in seen:
                    unique.append(b)
                    seen.add(isbn)
                    self._processing.add(isbn)

        try:
            semaphore = asyncio.Semaphore(self.max_concurrent)

            async def fetch_one(book: dict) -> CoverResult:
                async with semaphore:
                    isbn = book['isbn'].replace("-", "").replace(" ", "").strip()

                    if skip_existing and self.storage.exists(isbn):
                        return CoverResult(
                            isbn=isbn,
                            success=True,
                            local_path=self.storage.get_cover_path(isbn),
                            from_cache=True,
                            source=CoverSourceType.CACHE
                        )

                    result = await self.fetch(
                        isbn=book['isbn'],
                        book_title=book.get('title'),
                        book_author=book.get('author'),
                        book_genre=book.get('genre')
                    )

                    await asyncio.sleep(self.delay)
                    return result

            results = await asyncio.gather(*[fetch_one(b) for b in unique])

            isbn_to_result = {r.isbn: r for r in results}
            final = []
            for b in books:
                isbn = b['isbn'].replace("-", "").replace(" ", "").strip()
                final.append(isbn_to_result.get(isbn, CoverResult(
                    isbn=isbn,
                    success=False,
                    error="Not processed"
                )))
            return final

        finally:
            async with self._processing_lock:
                for b in unique:
                    isbn = b['isbn'].replace("-", "").replace(" ", "").strip()
                    self._processing.discard(isbn)

    def delete(self, isbn: str) -> bool:
        return self.storage.delete(isbn)

    def clear_cache(self) -> int:
        return self.storage.clear_cache()
