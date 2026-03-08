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
class DownloadResult:
    success: bool
    data: Optional[bytes] = None
    source: Optional[str] = None
    error: Optional[str] = None


class CoverDownloader:
    def __init__(self, timeout: float = 15.0, size: str = "M",):
        self.timeout = timeout
        self.size = size
        self._client: Optional[httpx.AsyncClient] = None

    @property
    def client(self) -> httpx.AsyncClient:
        if self._client is None:
            self._client = httpx.AsyncClient(timeout=self.timeout)
        return self._client

    async def download_from_openlibrary(self, isbn: str) -> DownloadResult:
        url = f"https://covers.openlibrary.org/b/isbn/{isbn}-{self.size}.jpg?default=false"
        try:
            response = await self.client.get(url)
            if response.status_code == 200:
                return DownloadResult(success=True, data=response.content, source=CoverSource.OPENLIBRARY.value)
            elif response.status_code == 404:
                return DownloadResult(success=False, error="Cover not found in Open Library", source=CoverSource.OPENLIBRARY.value)
            else:
                response.raise_for_status()
                return DownloadResult(success=False, error=f"Unexpected status: {response.status_code}", source=CoverSource.OPENLIBRARY.value)

        except httpx.HTTPStatusError as e:
            logger.warning(f"OpenLibrary HTTP error for {isbn}: {e}")
            return DownloadResult(success=False, error=str(e), source=CoverSource.OPENLIBRARY.value)
        except httpx.TimeoutException:
            logger.warning(f"OpenLibrary timeout for {isbn}")
            return DownloadResult(success=False, error="Timeout", source=CoverSource.OPENLIBRARY.value)
        except Exception as e:
            logger.error(f"OpenLibrary error for {isbn}: {e}")
            return DownloadResult(success=False, error=str(e), source=CoverSource.OPENLIBRARY.value)

    async def download_from_google(self, isbn: str, api_key: Optional[str] = None) -> DownloadResult:
        url = f"https://www.googleapis.com/books/v1/volumes?q=isbn:{isbn}"
        if api_key:
            url += f"&key={api_key}"

        try:
            response = await self.client.get(url)
            response.raise_for_status()
            data = response.json()

            if not data.get("items"):
                return DownloadResult(success=False, error="Book not found in Google Books", source=CoverSource.GOOGLE_BOOKS.value)
            image_links = data["items"][0]["volumeInfo"].get("imageLinks", {})
            if not image_links:
                return DownloadResult(success=False, error="No cover available in Google Books", source=CoverSource.GOOGLE_BOOKS.value)

            for size in ["extraLarge", "large", "medium", "small", "thumbnail"]:
                if size in image_links:
                    cover_url = image_links[size].replace("http://", "https://")
                    img_response = await self.client.get(cover_url)
                    img_response.raise_for_status()
                    return DownloadResult(success=True, data=img_response.content, source=CoverSource.GOOGLE_BOOKS.value)
            return DownloadResult(success=False, error="No suitable cover size found", source=CoverSource.GOOGLE_BOOKS.value)

        except httpx.HTTPStatusError as e:
            logger.warning(f"Google Books HTTP error for {isbn}: {e}")
            return DownloadResult(success=False, error=str(e), source=CoverSource.GOOGLE_BOOKS.value)
        except Exception as e:
            logger.error(f"Google Books error for {isbn}: {e}")
            return DownloadResult(success=False, error=str(e), source=CoverSource.GOOGLE_BOOKS.value)

    async def close(self) -> None:
        if self._client:
            await self._client.aclose()
            self._client = None
