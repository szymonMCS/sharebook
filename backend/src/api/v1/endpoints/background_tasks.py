import asyncio
import logging
from typing import Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from src.services.cover import get_cover_service
from src.api.v1.endpoints.websocket import notify_cover_updated, get_connection_manager
from database.repositories.book_repository import BookRepository
from src.services.book_enrichment_service import BookEnrichmentService
from sqlalchemy import update
from database.models import Book
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    pass

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
        
        cover_service = await get_cover_service()
        result = await cover_service.fetch_cover(isbn=isbn, book_title=title, book_author=author, book_genre=genre)
        
        if result.success and result.local_url:
            if db:
                from sqlalchemy import update
                from database.models import Book
                stmt = (update(Book).where(Book.id == book_id).values(cover_path=result.local_url))
                await db.execute(stmt)
                await db.commit()
            
            logger.info(
                f"[Background] Cover saved for book {book_id}: "
                f"{result.local_url} (source: {result.source})"
            )
            
            await notify_cover_updated(str(book_id), result.local_url)
            logger.info(f"[WebSocket] Sent cover_updated event for book {book_id}")
        else:
            logger.warning(
                f"[Background] Failed to get cover for book {book_id}: "
                f"{result.error or 'Unknown error'}"
            )
            
    except Exception as e:
        logger.error(f"[Background] Error in cover task for book {book_id}: {e}", exc_info=True)

async def enrich_and_fetch_cover_background(book_id: UUID, isbn: str, db: AsyncSession) -> None:
    try:
        logger.info(f"[Background] Starting combined enrichment for book {book_id}")
        
        enrichment_service = BookEnrichmentService(db)
        enrich_result = await enrichment_service.enrich_book(book_id)
        
        logger.info(f"[Background] Enrichment result: {enrich_result['status']}")
        
        book_repo = BookRepository(db)
        book = await book_repo.get_by_id(book_id)
        
        if not book:
            logger.error(f"[Background] Book {book_id} not found after enrichment")
            return
        
        cover_service = await get_cover_service()
        result = await cover_service.fetch_cover(isbn=isbn, book_title=book.title, book_author=book.author, book_genre=book.genre)
        
        if result.success and result.local_url:
            stmt = (update(Book).where(Book.id == book_id).values(cover_path=result.local_url))
            await db.execute(stmt)
            await db.commit()
            
            logger.info(f"[Background] Cover saved: {result.local_url} (source: {result.source})")
            
            await notify_cover_updated(str(book_id), result.local_url)
        else:
            logger.warning(f"[Background] Cover fetch failed: {result.error}")
            
    except Exception as e:
        logger.error(f"[Background] Error in combined task for book {book_id}: {e}", exc_info=True)
