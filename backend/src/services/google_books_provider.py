import logging
from typing import Optional, List

import httpx

from src.services.interfaces import IBookMetadataProvider, IMetadataProviderFactory, BookMetadata

logger = logging.getLogger(__name__)


class GoogleBooksProvider(IBookMetadataProvider):

    BASE_URL = "https://www.googleapis.com/books/v1"

    async def fetch_by_isbn(self, isbn: str) -> Optional[BookMetadata]:
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    f"{self.BASE_URL}/volumes",
                    params={"q": f"isbn:{isbn}"},
                    timeout=10.0
                )
                response.raise_for_status()
                data = response.json()

                if not data.get("items"):
                    logger.warning(f"No book found in Google Books for ISBN: {isbn}")
                    return None

                volume = data["items"][0]["volumeInfo"]
                return self._parse_volume(volume, isbn)

            except httpx.HTTPError as e:
                logger.error(f"HTTP error fetching from Google Books: {e}")
                return None
            except Exception as e:
                logger.error(f"Error parsing Google Books response: {e}")
                return None

    async def search_by_title(self, title: str, max_results: int = 10) -> List[BookMetadata]:
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    f"{self.BASE_URL}/volumes",
                    params={
                        "q": f"intitle:{title}",
                        "maxResults": max_results
                    },
                    timeout=10.0
                )
                response.raise_for_status()
                data = response.json()

                results = []
                for item in data.get("items", []):
                    volume = item["volumeInfo"]
                    isbn = self._extract_isbn(volume)
                    if isbn:
                        results.append(self._parse_volume(volume, isbn))

                return results

            except httpx.HTTPError as e:
                logger.error(f"HTTP error searching Google Books: {e}")
                return []
            except Exception as e:
                logger.error(f"Error parsing Google Books response: {e}")
                return []

    def _parse_volume(self, volume: dict, isbn: str) -> BookMetadata:
        published_date = volume.get("publishedDate", "")
        year = None
        if published_date:
            try:
                year = int(published_date[:4])
            except (ValueError, IndexError):
                pass

        image_links = volume.get("imageLinks", {})
        cover_url = image_links.get("thumbnail") or image_links.get("smallThumbnail")

        categories = volume.get("categories", [])
        genre = categories[0] if categories else None

        return BookMetadata(
            isbn=isbn,
            title=volume.get("title", "Unknown Title"),
            author=", ".join(volume.get("authors", ["Unknown Author"])),
            description=volume.get("description"),
            publisher=volume.get("publisher"),
            publication_year=year,
            page_count=volume.get("pageCount"),
            language=volume.get("language"),
            genre=genre,
            cover_url=cover_url
        )

    def _extract_isbn(self, volume: dict) -> Optional[str]:
        identifiers = volume.get("industryIdentifiers", [])
        for ident in identifiers:
            if ident.get("type") == "ISBN_13":
                return ident.get("identifier")
        for ident in identifiers:
            if ident.get("type") == "ISBN_10":
                return ident.get("identifier")
        return None


class GoogleBooksProviderFactory(IMetadataProviderFactory):

    def create_provider(self) -> IBookMetadataProvider:
        return GoogleBooksProvider()


class MockBookMetadataProvider(IBookMetadataProvider):

    def __init__(self, data: dict = None):
        self._data = data or {
            "9788328709576": BookMetadata(
                isbn="9788328709576",
                title="Wiedźmin - Ostatnie Życzenie",
                author="Andrzej Sapkowski",
                description="Zbiór opowiadań fantasy...",
                publisher="SuperNOWA",
                publication_year=2014,
                page_count=352,
                language="pl",
                genre="Fantasy"
            )
        }

    async def fetch_by_isbn(self, isbn: str) -> Optional[BookMetadata]:
        return self._data.get(isbn)

    async def search_by_title(self, title: str, max_results: int = 10) -> List[BookMetadata]:
        results = []
        for metadata in self._data.values():
            if title.lower() in metadata.title.lower():
                results.append(metadata)
        return results[:max_results]
