import logging
from uuid import UUID
from typing import List, Optional
from src.services.interfaces.books import IBookImportService, IBookMetadataProvider
from database.interfaces import IBookRepository
from src.schemas.book import BookResponse
from src.core.exceptions import BookNotFoundException
from src.core.validators import validate_isbn, normalize_isbn

logger = logging.getLogger(__name__)


class BookImportService(IBookImportService):
    def __init__(
        self,
        book_repo: IBookRepository,
        metadata_provider: IBookMetadataProvider,
        db_session: Optional[object] = None
    ):
        self._book_repo = book_repo
        self._provider = metadata_provider
        self._db = db_session

    async def import_by_isbn(self, isbn: str) -> BookResponse:
        is_valid, error = validate_isbn(isbn)
        if not is_valid:
            raise ValueError(f"Invalid ISBN: {error}")
        
        normalized_isbn = normalize_isbn(isbn)
        
        if self._db is not None and hasattr(self._book_repo, 'get_by_isbn_for_update'):
            existing = await self._book_repo.get_by_isbn_for_update(normalized_isbn)
            if existing:
                logger.info(f"Book with ISBN {normalized_isbn} already in catalog (locked)")
                return BookResponse.model_validate(existing)
        else:
            existing = await self._book_repo.get_by_isbn(normalized_isbn)
            if existing:
                logger.info(f"Book with ISBN {normalized_isbn} already in catalog")
                return BookResponse.model_validate(existing)

        metadata = await self._provider.fetch_by_isbn(normalized_isbn)
        if not metadata:
            raise BookNotFoundException(f"ISBN: {isbn}")

        book = await self._book_repo.create(
            isbn=metadata.isbn,
            title=metadata.title,
            author=metadata.author,
            description=metadata.description,
            publisher=metadata.publisher,
            publication_year=metadata.publication_year,
            page_count=metadata.page_count,
            language=metadata.language or "pl",
            genre=metadata.genre,
            cover_url=getattr(metadata, 'cover_url', None)
        )
        logger.info(f"Book imported from external source: {book.id} (ISBN: {normalized_isbn})")
        return BookResponse.model_validate(book)

    async def enrich_book_data(self, book_id: UUID) -> BookResponse:
        book = await self._book_repo.get_by_id(book_id)
        if not book:
            raise BookNotFoundException(book_id)

        if not book.isbn:
            raise ValueError("Book has no ISBN to fetch metadata")

        metadata = await self._provider.fetch_by_isbn(book.isbn)
        if not metadata:
            raise BookNotFoundException(f"No metadata found for ISBN: {book.isbn}")

        update_data = {}
        if not book.title or book.title == "Wczytywanie...":
            update_data["title"] = metadata.title
        if not book.author:
            update_data["author"] = metadata.author
        if not book.description:
            update_data["description"] = metadata.description
        if not book.publisher:
            update_data["publisher"] = metadata.publisher
        if not book.publication_year:
            update_data["publication_year"] = metadata.publication_year
        if not book.page_count:
            update_data["page_count"] = metadata.page_count
        if not book.genre:
            update_data["genre"] = metadata.genre
        if not book.language or book.language == "pl":
            update_data["language"] = metadata.language or "pl"
        
        if not book.cover_url and getattr(metadata, 'cover_url', None):
            update_data["cover_url"] = metadata.cover_url

        if update_data:
            updated = await self._book_repo.update(book_id, update_data)
            logger.info(f"Book {book_id} enriched with metadata")
            return BookResponse.model_validate(updated)
        
        return BookResponse.model_validate(book)

    async def search_and_import(self, query: str, limit: int = 5, max_imports: int = 10) -> List[BookResponse]:
        metadata_list = await self._provider.search_by_title(query, limit)
        
        imported = []
        for i, metadata in enumerate(metadata_list):
            if i >= max_imports:
                break
            try:
                book = await self.import_by_isbn(metadata.isbn)
                imported.append(book)
            except Exception as e:
                logger.warning(f"Failed to import book with ISBN {metadata.isbn}: {e}")
                continue
        
        logger.info(f"Imported {len(imported)} books from search: {query}")
        return imported
