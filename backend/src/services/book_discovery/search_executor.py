import logging
from typing import Optional
from dataclasses import dataclass
import httpx

logger = logging.getLogger(__name__)


@dataclass
class CoverResult:
    url: Optional[str]
    source: Optional[str]
    error: Optional[str] = None


class SearchExecutor:
    def __init__(self, timeout: float = 5.0):
        self.timeout = timeout

    async def get_cover_from_openlibrary(self, isbn: str) -> CoverResult:
        logger.info(f"[OpenLibrary] Searching cover for ISBN: {isbn}")

        if not isbn:
            logger.warning("[OpenLibrary] Missing ISBN")
            return CoverResult(url=None, source=None, error="Missing ISBN")

        url = f"https://covers.openlibrary.org/b/isbn/{isbn}-M.jpg"

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.head(url, follow_redirects=True)
                logger.info(f"[OpenLibrary] Status: {response.status_code}")

                if response.status_code == 200:
                    logger.info(f"[OpenLibrary] Found cover: {url}")
                    return CoverResult(url=url, source="openlibrary")
                else:
                    logger.warning(f"[OpenLibrary] No cover (status: {response.status_code})")
                    return CoverResult(url=None, source=None, error=f"Status {response.status_code}")

        except Exception as e:
            logger.error(f"[OpenLibrary] Error: {e}")
            return CoverResult(url=None, source=None, error=str(e))

    async def find_cover(self, isbn: str) -> CoverResult:
        result = await self.get_cover_from_openlibrary(isbn)
        if result.url:
            return result

        return CoverResult(url=None, source=None, error="Not found")
