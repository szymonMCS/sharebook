import logging
from typing import Optional
from dataclasses import dataclass
from enum import Enum
import httpx

logger = logging.getLogger(__name__)


class CoverSource(Enum):
    OPENLIBRARY = "openlibrary"
    GOOGLE_BOOKS = "google_books"


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
                    return CoverResult(url=url, source=CoverSource.OPENLIBRARY.value)
                else:
                    logger.warning(f"[OpenLibrary] No cover (status: {response.status_code})")
                    return CoverResult(url=None, source=None, error=f"Status {response.status_code}")

        except Exception as e:
            logger.error(f"[OpenLibrary] Error: {e}")
            return CoverResult(url=None, source=None, error=str(e))

    async def get_cover_from_google(self, isbn: str) -> CoverResult:
        logger.info(f"[GoogleBooks] Searching cover for ISBN: {isbn}")

        if not isbn:
            logger.warning("[GoogleBooks] Missing ISBN")
            return CoverResult(url=None, source=None, error="Missing ISBN")

        url = f"https://www.googleapis.com/books/v1/volumes?q=isbn:{isbn}"

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(url)
                data = response.json()

                if not data.get("items"):
                    logger.warning("[GoogleBooks] No results found")
                    return CoverResult(url=None, source=None, error="No results")

                image_links = data["items"][0]["volumeInfo"].get("imageLinks", {})
                if not image_links:
                    logger.warning("[GoogleBooks] No image links in response")
                    return CoverResult(url=None, source=None, error="No images")

                for size in ["extraLarge", "large", "medium", "small", "thumbnail"]:
                    if size in image_links:
                        cover_url = image_links[size].replace("http://", "https://")
                        logger.info(f"[GoogleBooks] Found cover ({size}): {cover_url}")
                        return CoverResult(url=cover_url, source=CoverSource.GOOGLE_BOOKS.value)

                return CoverResult(url=None, source=None, error="No suitable size")

        except Exception as e:
            logger.error(f"[GoogleBooks] Error: {e}")
            return CoverResult(url=None, source=None, error=str(e))

    async def find_cover(self, isbn: str) -> CoverResult:
        result = await self.get_cover_from_openlibrary(isbn)
        if result.url:
            return result

        result = await self.get_cover_from_google(isbn)
        if result.url:
            return result

        return CoverResult(url=None, source=None, error="Not found in any source")
