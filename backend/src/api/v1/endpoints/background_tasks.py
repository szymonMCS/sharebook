import asyncio
import logging
from typing import Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from src.services.cover import get_cover_service
from src.api.v1.endpoints.system.websocket import notify_cover_updated, notify_cover_status, notify_book_enriched
from database.repositories.book_repository import BookRepository
from src.services.book_discovery import UnifiedBookSearch
from sqlalchemy import update
from database.models import Book

logger = logging.getLogger(__name__)

async def download_book_cover_background(
    book_id: UUID,
    isbn: str,
    title: str,
    author: Optional[str] = None,
    genre: Optional[str] = None,
    db: Optional[AsyncSession] = None
) -> None:
    await asyncio.sleep(1)
    
    try:
        logger.info(f"[Background] Starting cover fetch for book {book_id} (ISBN: {isbn})")
        await notify_cover_status(str(book_id), "processing")
        
        cover_service = await get_cover_service()
        result = await cover_service.fetch_cover(isbn=isbn, book_title=title, book_author=author, book_genre=genre)
        
        if result.success and result.local_url:
            if db:
                stmt = (update(Book).where(Book.id == book_id).values(cover_url=result.local_url))
                await db.execute(stmt)
                await db.commit()
            logger.info(f"[Background] Cover saved for book {book_id}: "f"{result.local_url} (source: {result.source})")
            
            await notify_cover_status(str(book_id), "completed", result.local_url)
            await notify_cover_updated(str(book_id), result.local_url)
            logger.info(f"[WebSocket] Sent cover events for book {book_id}")
        else:
            logger.warning(
                f"[Background] Failed to get cover for book {book_id}: "
                f"{result.error or 'Unknown error'}"
            )
            await notify_cover_status(str(book_id), "failed")
            
    except Exception as e:
        logger.error(f"[Background] Error in cover task for book {book_id}: {e}", exc_info=True)
        await notify_cover_status(str(book_id), "failed")

async def enrich_and_fetch_cover_background(book_id: UUID, isbn: str, db: AsyncSession) -> None:
    logger.info(f"[Background] Starting enrichment for book {book_id}")
    try:
        await notify_cover_status(str(book_id), "processing")
        search = UnifiedBookSearch()
        result = await search.search_by_isbn(isbn)
        
        if result.success and result.data:
            book_repo = BookRepository(db)
            book = await book_repo.get_by_id(book_id)
            
            if not book:
                logger.error(f"[Background] Book {book_id} not found")
                await notify_cover_status(str(book_id), "failed")
                return
            
            data = result.data
            update_values = {}
            
            if data.get('full_title') and book.title in ["", "Wczytywanie...", "Unknown"]:
                update_values['title'] = data['full_title']
            if data.get('author') and (not book.author or book.author == ""):
                update_values['author'] = data['author']
            if data.get('short_description') and (not book.description or book.description == ""):
                update_values['description'] = data['short_description']
            if data.get('isbn_13') and (not book.isbn or book.isbn == ""):
                update_values['isbn'] = data['isbn_13']
            if data.get('page_count') and not book.page_count:
                update_values['page_count'] = data['page_count']
            if data.get('publication_year') and not book.publication_year:
                update_values['publication_year'] = data['publication_year']
            if data.get('genre') and (not book.genre or book.genre == ""):
                update_values['genre'] = data['genre']
            if data.get('language') and (not book.language or book.language == ""):
                update_values['language'] = data['language']
            if data.get('publisher') and (not book.publisher or book.publisher == ""):
                update_values['publisher'] = data['publisher']
            
            if update_values:
                stmt = update(Book).where(Book.id == book_id).values(**update_values)
                await db.execute(stmt)
                await db.commit()
                logger.info(f"[Background] Updated book {book_id} with {len(update_values)} fields")
                
                enriched_data = {k: v for k, v in update_values.items()}
                await notify_book_enriched(str(book_id), enriched_data)
            
            cover_url = data.get('cover_image_url')
            if cover_url and (not book.cover_url or book.cover_url == ""):
                await notify_cover_status(str(book_id), "processing")
                cover_service = await get_cover_service()
                cover_result = await cover_service.fetch_cover(
                    isbn=isbn, 
                    book_title=data.get('full_title', book.title), 
                    book_author=data.get('author', book.author)
                )
                
                if cover_result.success and cover_result.local_url:
                    stmt = update(Book).where(Book.id == book_id).values(cover_url=cover_result.local_url)
                    await db.execute(stmt)
                    await db.commit()
                    logger.info(f"[Background] Cover saved: {cover_result.local_url}")
                    await notify_cover_status(str(book_id), "completed", cover_result.local_url)
                    await notify_cover_updated(str(book_id), cover_result.local_url)
                else:
                    logger.warning(f"[Background] Failed to fetch cover: {cover_result.error}")
                    await notify_cover_status(str(book_id), "failed")
            else:
                await notify_cover_status(str(book_id), "completed")
        else:
            logger.warning(f"[Background] Search failed for book {book_id}: {result.error}")
            await notify_cover_status(str(book_id), "failed")
            
    except Exception as e:
        logger.error(f"[Background] Error in enrichment task for book {book_id}: {e}", exc_info=True)
        await notify_cover_status(str(book_id), "failed")
