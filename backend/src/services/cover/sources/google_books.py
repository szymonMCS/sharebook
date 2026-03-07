import asyncio
import logging
from src.services.cover.interfaces import ICoverSource, CoverResult, CoverSourceType
from src.services.google_books_client import get_google_books_client

logger = logging.getLogger(__name__)


class GoogleBooksSource(ICoverSource):
    PRIORITY = 2

    def is_available(self) -> bool:
        return True

    def get_priority(self) -> int:
        return self.PRIORITY

    @property
    def source_type(self) -> CoverSourceType:
        return CoverSourceType.GOOGLE_BOOKS

    async def fetch_cover(self, isbn: str, book_title: str | None = None, book_author: str | None = None, book_genre: str | None = None) -> CoverResult:
        clean_isbn = isbn.replace("-", "").replace(" ", "").strip()

        try:
            client = get_google_books_client()
            image_data = await client.download_cover(clean_isbn)

            if image_data:
                return CoverResult(
                    isbn=clean_isbn,
                    success=True,
                    data=image_data,
                    source=CoverSourceType.GOOGLE_BOOKS
                )
            return CoverResult(
                isbn=clean_isbn,
                success=False,
                error="Not found",
                source=CoverSourceType.GOOGLE_BOOKS
            )
        except asyncio.TimeoutError:
            return CoverResult(
                isbn=clean_isbn,
                success=False,
                error="Timeout",
                source=CoverSourceType.GOOGLE_BOOKS
            )
        except Exception as e:
            logger.warning(f"Google Books error for {isbn}: {e}")
            return CoverResult(
                isbn=clean_isbn,
                success=False,
                error=str(e),
                source=CoverSourceType.GOOGLE_BOOKS
            )
