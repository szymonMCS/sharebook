import logging
from typing import Optional
from dataclasses import dataclass
import httpx

logger = logging.getLogger(__name__)


@dataclass
class DownloadResult:
    success: bool
    data: Optional[bytes] = None
    source: Optional[str] = None
    error: Optional[str] = None


class CoverDownloader:
    def __init__(self, timeout: float = 15.0, size: str = "M"):
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
                return DownloadResult(success=True, data=response.content, source="openlibrary")
            elif response.status_code == 404:
                return DownloadResult(success=False, error="Cover not found in Open Library", source="openlibrary")
            else:
                response.raise_for_status()
                return DownloadResult(success=False, error=f"Unexpected status: {response.status_code}", source="openlibrary")

        except httpx.HTTPStatusError as e:
            logger.warning(f"OpenLibrary HTTP error for {isbn}: {e}")
            return DownloadResult(success=False, error=str(e), source="openlibrary")
        except httpx.TimeoutException:
            logger.warning(f"OpenLibrary timeout for {isbn}")
            return DownloadResult(success=False, error="Timeout", source="openlibrary")
        except Exception as e:
            logger.error(f"OpenLibrary error for {isbn}: {e}")
            return DownloadResult(success=False, error=str(e), source="openlibrary")

    async def close(self) -> None:
        if self._client:
            await self._client.aclose()
            self._client = None
