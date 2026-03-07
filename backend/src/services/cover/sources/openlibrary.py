import asyncio
import logging
import aiohttp
from src.services.cover.interfaces import ICoverSource, CoverResult, CoverSourceType

logger = logging.getLogger(__name__)


class OpenLibrarySource(ICoverSource):
    PRIORITY = 1

    def __init__(self, size: str = "M", timeout: float = 15.0):
        self.size = size
        self.timeout = timeout
        self._session: aiohttp.ClientSession | None = None

    @property
    def source_type(self) -> CoverSourceType:
        return CoverSourceType.OPENLIBRARY

    def is_available(self) -> bool:
        return True

    def get_priority(self) -> int:
        return self.PRIORITY

    async def _get_session(self) -> aiohttp.ClientSession:
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=self.timeout))
        return self._session

    async def fetch_cover(self, isbn: str, book_title: str | None = None, book_author: str | None = None, book_genre: str | None = None) -> CoverResult:
        clean_isbn = isbn.replace("-", "").replace(" ", "").strip()
        url = f"https://covers.openlibrary.org/b/isbn/{clean_isbn}-{self.size}.jpg?default=false"

        try:
            session = await self._get_session()
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.read()
                    return CoverResult(
                        isbn=clean_isbn,
                        success=True,
                        data=data,
                        source=CoverSourceType.OPENLIBRARY
                    )
                elif response.status == 404:
                    return CoverResult(
                        isbn=clean_isbn,
                        success=False,
                        error="Cover not found",
                        source=CoverSourceType.OPENLIBRARY
                    )
                else:
                    return CoverResult(
                        isbn=clean_isbn,
                        success=False,
                        error=f"HTTP {response.status}",
                        source=CoverSourceType.OPENLIBRARY
                    )
        except asyncio.TimeoutError:
            return CoverResult(
                isbn=clean_isbn,
                success=False,
                error="Timeout",
                source=CoverSourceType.OPENLIBRARY
            )
        except Exception as e:
            logger.warning(f"OpenLibrary error for {isbn}: {e}")
            return CoverResult(
                isbn=clean_isbn,
                success=False,
                error=str(e),
                source=CoverSourceType.OPENLIBRARY
            )
