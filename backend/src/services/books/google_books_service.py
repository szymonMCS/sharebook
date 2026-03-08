import logging
from typing import Optional, Dict, Any, List
import aiohttp
from src.config import settings
from src.services.interfaces.books import IBookMetadataProvider, IMetadataProviderFactory, BookMetadata
from src.schemas.book import BookCreate

logger = logging.getLogger(__name__)

class GoogleBooksClient:
    BASE_URL = "https://www.googleapis.com/books/v1/volumes"
    
    def __init__(self, api_key: Optional[str] = None, timeout: int = 10):
        self.api_key = api_key or settings.GOOGLE_BOOKS_API_KEY
        self.timeout = timeout
    
    async def fetch_by_isbn(self, isbn: str) -> Optional[Dict[str, Any]]:
        clean_isbn = isbn.replace("-", "").replace(" ", "").strip()
        url = f"{self.BASE_URL}?q=isbn:{clean_isbn}"
        
        if self.api_key:
            url += f"&key={self.api_key}"
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=self.timeout) as response:
                    if response.status != 200:
                        logger.warning(f"Google Books API error: {response.status}")
                        return None
                    data = await response.json()
                    if not data.get("items"):
                        return None
                    return self._parse_volume_info(data["items"][0]["volumeInfo"])
                    
        except Exception as e:
            logger.error(f"Error fetching from Google Books: {e}")
            return None
    
    async def search_by_title(self, title: str, max_results: int = 10) -> List[Dict[str, Any]]:
        url = f"{self.BASE_URL}?q=intitle:{title}&maxResults={min(max_results, 40)}"
        
        if self.api_key:
            url += f"&key={self.api_key}"
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=self.timeout) as response:
                    if response.status != 200:
                        return []
                    
                    data = await response.json()
                    items = data.get("items", [])
                    return [self._parse_volume_info(item["volumeInfo"]) for item in items]
                    
        except Exception as e:
            logger.error(f"Error searching Google Books: {e}")
            return []
    
    async def download_cover(self, isbn: str, size_preference: List[str] = None) -> Optional[bytes]:
        if size_preference is None:
            size_preference = ["extraLarge", "large", "medium", "small", "thumbnail"]
        
        clean_isbn = isbn.replace("-", "").replace(" ", "").strip()
        url = f"{self.BASE_URL}?q=isbn:{clean_isbn}"
        
        if self.api_key:
            url += f"&key={self.api_key}"
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=self.timeout) as response:
                    if response.status != 200:
                        return None
                    data = await response.json()
                    if not data.get("items"):
                        return None
                    image_links = data["items"][0]["volumeInfo"].get("imageLinks", {})
                    for size in size_preference:
                        if size in image_links:
                            cover_url = image_links[size].replace("http://", "https://")
                            try:
                                async with session.get(cover_url, timeout=self.timeout) as img_response:
                                    if img_response.status == 200:
                                        return await img_response.read()
                            except Exception as e:
                                logger.debug(f"Failed to download {size}: {e}")
                                continue
                    return None
                    
        except Exception as e:
            logger.error(f"Error downloading cover from Google Books: {e}")
            return None
    
    def _parse_volume_info(self, volume_info: Dict[str, Any]) -> Dict[str, Any]:
        isbn = ""
        for identifier in volume_info.get("industryIdentifiers", []):
            if identifier.get("type") in ["ISBN_13", "ISBN_10"]:
                isbn = identifier.get("identifier", "")
                break
        
        cover_url = None
        image_links = volume_info.get("imageLinks", {})
        for size in ["extraLarge", "large", "medium", "small", "thumbnail"]:
            if size in image_links:
                cover_url = image_links[size].replace("http://", "https://")
                break
        
        pub_year = None
        pub_date = volume_info.get("publishedDate", "")
        if pub_date and len(pub_date) >= 4:
            try:
                pub_year = int(pub_date[:4])
            except ValueError:
                pass
        
        authors = volume_info.get("authors", [])
        author = authors[0] if authors else "Unknown"
        
        categories = volume_info.get("categories", [])
        genre = categories[0] if categories else None
        
        return {
            "isbn": isbn,
            "title": volume_info.get("title", "Unknown Title"),
            "author": author,
            "description": volume_info.get("description", ""),
            "publisher": volume_info.get("publisher"),
            "publication_year": pub_year,
            "page_count": volume_info.get("pageCount"),
            "language": volume_info.get("language", "pl"),
            "genre": genre,
            "cover_url": cover_url,
        }


class GoogleBooksService(IBookMetadataProvider):
    def __init__(self, client: Optional[GoogleBooksClient] = None):
        self._client = client or GoogleBooksClient()
    
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
    
    def to_book_create(self, book_data: Dict[str, Any]) -> BookCreate:
        return BookCreate(
            title=book_data.get("title", ""),
            author=book_data.get("author", "Unknown"),
            isbn=book_data.get("isbn", ""),
            description=book_data.get("description"),
            publisher=book_data.get("publisher"),
            publication_year=book_data.get("publication_year"),
            page_count=book_data.get("page_count"),
            language=book_data.get("language", "pl"),
            genre=book_data.get("genre"),
            cover_url=book_data.get("cover_url"),
        )


class GoogleBooksServiceFactory(IMetadataProviderFactory): 
    def create_provider(self) -> IBookMetadataProvider:
        return GoogleBooksService()


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

_google_books_service: Optional[GoogleBooksService] = None

def get_google_books_service() -> GoogleBooksService:
    global _google_books_service
    if _google_books_service is None:
        _google_books_service = GoogleBooksService()
    return _google_books_service
