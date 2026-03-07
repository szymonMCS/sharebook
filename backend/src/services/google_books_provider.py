import logging
from typing import Optional, List

from src.services.interfaces.books import IBookMetadataProvider, IMetadataProviderFactory, BookMetadata
from src.services.google_books_client import GoogleBooksClient, get_google_books_client

logger = logging.getLogger(__name__)


class GoogleBooksProvider(IBookMetadataProvider):
    def __init__(self, client: Optional[GoogleBooksClient] = None):
        self._client = client or get_google_books_client()

    async def fetch_by_isbn(self, isbn: str) -> Optional[BookMetadata]:
        data = await self._client.fetch_by_isbn(isbn)
        if not data:
            return None
        
        return BookMetadata(
            isbn=data.get("isbn", isbn),
            title=data.get("title", "Unknown Title"),
            author=data.get("author", "Unknown Author"),
            description=data.get("description"),
            publisher=data.get("publisher"),
            publication_year=data.get("publication_year"),
            page_count=data.get("page_count"),
            language=data.get("language"),
            genre=data.get("genre"),
            cover_url=data.get("cover_url")
        )

    async def search_by_title(self, title: str, max_results: int = 10) -> List[BookMetadata]:
        results = await self._client.search_by_title(title, max_results)
        
        return [
            BookMetadata(
                isbn=data.get("isbn", ""),
                title=data.get("title", "Unknown Title"),
                author=data.get("author", "Unknown Author"),
                description=data.get("description"),
                publisher=data.get("publisher"),
                publication_year=data.get("publication_year"),
                page_count=data.get("page_count"),
                language=data.get("language"),
                genre=data.get("genre"),
                cover_url=data.get("cover_url")
            )
            for data in results
        ]


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
