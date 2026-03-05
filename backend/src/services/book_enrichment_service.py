import logging
from typing import Optional, Dict, Any
from uuid import UUID
from openai import AsyncOpenAI
from sqlalchemy.ext.asyncio import AsyncSession
from src.config import settings
from database.repositories.book_repository import BookRepository

logger = logging.getLogger(__name__)


class GoogleBooksService:
    def __init__(self):
        self.base_url = "https://www.googleapis.com/books/v1/volumes"
    
    async def fetch_by_isbn(self, isbn: str) -> Optional[Dict[str, Any]]:
        import aiohttp
        
        clean_isbn = isbn.replace("-", "").replace(" ", "").strip()
        url = f"{self.base_url}?q=isbn:{clean_isbn}"
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=10) as response:
                    if response.status != 200:
                        return None
                    
                    data = await response.json()
                    if not data.get("items"):
                        return None
                    
                    volume = data["items"][0]["volumeInfo"]
                    
                    image_links = volume.get("imageLinks", {})
                    cover_url = None
                    for size in ["extraLarge", "large", "medium", "small", "thumbnail"]:
                        if size in image_links:
                            cover_url = image_links[size].replace("http://", "https://")
                            break
                    
                    categories = volume.get("categories", [])
                    genre = categories[0] if categories else None
                    
                    return {
                        "title": volume.get("title"),
                        "authors": volume.get("authors", []),
                        "description": volume.get("description"),
                        "publisher": volume.get("publisher"),
                        "publication_year": volume.get("publishedDate", ":")[:4] if volume.get("publishedDate") else None,
                        "page_count": volume.get("pageCount"),
                        "genre": genre,
                        "cover_url": cover_url,
                        "language": volume.get("language"),
                    }
        except Exception as e:
            logger.warning(f"[GoogleBooks] Error fetching {isbn}: {e}")
            return None


class BookEnrichmentService:
    def __init__(self, db: AsyncSession):
        self._db = db
        self._book_repo = BookRepository(db)
        self._client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self._model = settings.OPENAI_CHAT_MODEL
        self._google_service = GoogleBooksService()
    
    async def enrich_book(self, book_id: UUID) -> Dict[str, Any]:
        book = await self._book_repo.get_by_id(book_id)
        if not book:
            return {"status": "failed", "error": "Book not found"}
        
        changes = []
        
        try:
            google_data = None
            if book.isbn:
                try:
                    google_data = await self._google_service.fetch_by_isbn(book.isbn)
                    if google_data:
                        logger.info(f"[Enrich] Google Books data found for {book.isbn}")
                except Exception as e:
                    logger.warning(f"[Enrich] Google Books failed for {book.isbn}: {e}")
            
            current_desc_len = len(book.description) if book.description else 0
            
            if current_desc_len < 500:
                enriched_description = await self._generate_description(
                    title=book.title,
                    author=book.author,
                    isbn=book.isbn,
                    existing_description=book.description,
                    google_description=google_data.get("description") if google_data else None,
                    genre=book.genre or (google_data.get("genre") if google_data else None),
                )
                
                if enriched_description and len(enriched_description) > current_desc_len:
                    book.description = enriched_description
                    changes.append(f"description: {current_desc_len} → {len(enriched_description)} chars")
                    logger.info(f"[Enrich] Description enriched for book {book_id}")
            
            if google_data:
                if not book.publisher and google_data.get("publisher"):
                    book.publisher = google_data["publisher"]
                    changes.append("publisher")
                
                if not book.publication_year and google_data.get("publication_year"):
                    try:
                        year = int(google_data["publication_year"])
                        book.publication_year = year
                        changes.append("publication_year")
                    except (ValueError, TypeError):
                        pass
                
                if not book.page_count and google_data.get("page_count"):
                    try:
                        pages = int(google_data["page_count"])
                        book.page_count = pages
                        changes.append("page_count")
                    except (ValueError, TypeError):
                        pass
                
                if not book.genre and google_data.get("genre"):
                    book.genre = google_data["genre"]
                    changes.append("genre")
            
            if book.title in ["Wczytywanie...", "", None] and book.isbn:
                new_title, new_author = await self._generate_title_author(book.isbn)
                if new_title:
                    book.title = new_title
                    changes.append(f"title: 'Wczytywanie...' → '{new_title}'")
                if new_author:
                    book.author = new_author
                    changes.append("author: updated")
            
            if changes:
                await self._db.commit()
                await self._db.refresh(book)
                logger.info(f"[Enrich] Book {book_id} enriched: {', '.join(changes)}")
                return {
                    "status": "enriched",
                    "book_id": str(book_id),
                    "isbn": book.isbn,
                    "changes": changes
                }
            else:
                return {
                    "status": "skipped",
                    "book_id": str(book_id),
                    "reason": "No enrichment needed"
                }
                
        except Exception as e:
            logger.exception(f"[Enrich] Failed to enrich book {book_id}: {e}")
            return {"status": "failed", "book_id": str(book_id), "error": str(e)}
    
    async def _generate_description(
        self,
        title: str,
        author: str,
        isbn: Optional[str],
        existing_description: Optional[str],
        google_description: Optional[str],
        genre: Optional[str],
    ) -> Optional[str]:
        context_parts = []
        if title and title != "Wczytywanie...":
            context_parts.append(f"Tytuł: {title}")
        if author:
            context_parts.append(f"Autor: {author}")
        if isbn:
            context_parts.append(f"ISBN: {isbn}")
        if genre:
            context_parts.append(f"Gatunek: {genre}")
        if google_description:
            context_parts.append(f"Opis z Google Books: {google_description[:500]}")
        if existing_description:
            context_parts.append(f"Istniejący opis: {existing_description[:300]}")
        
        context = "\n".join(context_parts)
        
        prompt = f"""Jesteś profesjonalnym bibliotekarzem. Napisz opis książki w języku polskim.

DANE KSIĄŻKI:
{context}

ZASADY:
1. Opis powinien być bogaty i szczegółowy (800-1200 znaków)
2. Napisz profesjonalnym, ale przystępnym językiem
3. Zawieraj: o czym jest książka, dla kogo jest przeznaczona, dlaczego warto przeczytać
4. Nie wymyślaj faktów - użyj tylko podanego kontekstu
5. Jeśli brak szczegółów, napisz ogólny opis oparty na tytule i autorze

Napisz TYLKO opis, bez nagłówków, bez cudzysłowów na początku i końca."""

        try:
            response = await self._client.chat.completions.create(
                model=self._model,
                messages=[
                    {"role": "system", "content": "Jesteś bibliotekarzem piszącym opisy książek."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=800,
            )
            
            description = response.choices[0].message.content.strip()
            
            description = description.strip('"\'')
            if description.startswith("Opis:"):
                description = description[5:].strip()
            
            if len(description) < 200:
                logger.warning(f"[Enrich] Generated description too short: {len(description)} chars")
                return None
            
            return description
            
        except Exception as e:
            logger.error(f"[Enrich] OpenAI description generation failed: {e}")
            return None
    
    async def _generate_title_author(self, isbn: str) -> tuple[Optional[str], Optional[str]]:
        
        prompt = f"""Podaj tytuł i autora książki o ISBN: {isbn}

Odpowiedź w formacie:
Tytuł: [tytuł książki]
Autor: [autor książki]

Jeśli nie znasz tego ISBN, napisz "Nieznane"."""

        try:
            response = await self._client.chat.completions.create(
                model=self._model,
                messages=[
                    {"role": "system", "content": "Jesteś bibliotekarzem z dostępem do katalogu ISBN."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=200,
            )
            
            content = response.choices[0].message.content.strip()
            
            title = None
            author = None
            
            for line in content.split("\n"):
                if line.startswith("Tytuł:"):
                    title = line[6:].strip()
                elif line.startswith("Autor:"):
                    author = line[6:].strip()
            
            return title, author
            
        except Exception as e:
            logger.error(f"[Enrich] OpenAI title/author generation failed: {e}")
            return None, None

async def enrich_book_background(book_id: UUID, db: AsyncSession) -> None:
    service = BookEnrichmentService(db)
    result = await service.enrich_book(book_id)
    logger.info(f"[Background] Enrichment result for {book_id}: {result['status']}")
