import asyncio
import logging
from typing import Optional
from dataclasses import dataclass
from enum import Enum
import aiohttp

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

    async def download_from_openlibrary(self, isbn: str) -> DownloadResult:
        clean_isbn = isbn.replace("-", "").replace(" ", "").strip()
        url = f"https://covers.openlibrary.org/b/isbn/{clean_isbn}-{self.size}.jpg?default=false"

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=self.timeout) as response:
                    if response.status == 200:
                        data = await response.read()
                        return DownloadResult(
                            success=True,
                            data=data,
                            source=CoverSource.OPENLIBRARY.value
                        )
                    elif response.status == 404:
                        return DownloadResult(
                            success=False,
                            error="Cover not found in Open Library",
                            source=CoverSource.OPENLIBRARY.value
                        )
                    else:
                        return DownloadResult(
                            success=False,
                            error=f"Unexpected status: {response.status}",
                            source=CoverSource.OPENLIBRARY.value
                        )

        except aiohttp.ClientError as e:
            logger.warning(f"[CoverDownloader] OpenLibrary HTTP error for {isbn}: {e}")
            return DownloadResult(success=False, error=str(e), source=CoverSource.OPENLIBRARY.value)
        except asyncio.TimeoutError:
            logger.warning(f"[CoverDownloader] OpenLibrary timeout for {isbn}")
            return DownloadResult(success=False, error="Timeout", source=CoverSource.OPENLIBRARY.value)
        except Exception as e:
            logger.error(f"[CoverDownloader] OpenLibrary error for {isbn}: {e}")
            return DownloadResult(success=False, error=str(e), source=CoverSource.OPENLIBRARY.value)

    async def download_from_google(self, isbn: str, api_key: Optional[str] = None) -> DownloadResult:
        clean_isbn = isbn.replace("-", "").replace(" ", "").strip()
        url = f"https://www.googleapis.com/books/v1/volumes?q=isbn:{clean_isbn}"
        if api_key:
            url += f"&key={api_key}"

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=self.timeout) as response:
                    if response.status != 200:
                        return DownloadResult(
                            success=False,
                            error=f"Google Books API error: {response.status}",
                            source=CoverSource.GOOGLE_BOOKS.value
                        )
                    
                    data = await response.json()

                    if not data.get("items"):
                        return DownloadResult(
                            success=False,
                            error="Book not found in Google Books",
                            source=CoverSource.GOOGLE_BOOKS.value
                        )

                    image_links = data["items"][0]["volumeInfo"].get("imageLinks", {})
                    if not image_links:
                        return DownloadResult(
                            success=False,
                            error="No cover available in Google Books",
                            source=CoverSource.GOOGLE_BOOKS.value
                        )

                    for size in ["extraLarge", "large", "medium", "small", "thumbnail"]:
                        if size in image_links:
                            cover_url = image_links[size].replace("http://", "https://")
                            try:
                                async with session.get(cover_url, timeout=self.timeout) as img_response:
                                    if img_response.status == 200:
                                        img_data = await img_response.read()
                                        return DownloadResult(
                                            success=True,
                                            data=img_data,
                                            source=CoverSource.GOOGLE_BOOKS.value
                                        )
                            except Exception as e:
                                logger.debug(f"[CoverDownloader] Failed to download {size}: {e}")
                                continue

                    return DownloadResult(
                        success=False,
                        error="No suitable cover size found",
                        source=CoverSource.GOOGLE_BOOKS.value
                    )

        except aiohttp.ClientError as e:
            logger.warning(f"[CoverDownloader] Google Books HTTP error for {isbn}: {e}")
            return DownloadResult(success=False, error=str(e), source=CoverSource.GOOGLE_BOOKS.value)
        except Exception as e:
            logger.error(f"[CoverDownloader] Google Books error for {isbn}: {e}")
            return DownloadResult(success=False, error=str(e), source=CoverSource.GOOGLE_BOOKS.value)
