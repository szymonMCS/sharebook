import logging
from typing import List, Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from database.repositories.book_repository import BookRepository
from src.services.interfaces import (
    IEnrichmentOrchestrator,
    IEnrichmentAdapter,
    IEnrichmentStrategy,
    EnrichmentContext,
    EnrichmentResult,
)

logger = logging.getLogger(__name__)


class EnrichmentOrchestrator(IEnrichmentOrchestrator):
    def __init__(self, db: AsyncSession, adapters: List[IEnrichmentAdapter], strategy: IEnrichmentStrategy, book_repo=None):
        self._db = db
        self._adapters = [a for a in adapters if a.is_available()]
        self._strategy = strategy
        self._book_repo = book_repo or BookRepository(db)

    async def enrich_book(self, book_id: UUID) -> EnrichmentResult:
        book = await self._book_repo.get_by_id(book_id)
        if not book:
            return EnrichmentResult(
                book_id=book_id,
                status="failed",
                error="Book not found"
            )

        context = EnrichmentContext(
            book_id=book_id,
            isbn=book.isbn,
            current_title=book.title,
            current_author=book.author,
            current_description=book.description,
            current_genre=book.genre,
            current_publisher=book.publisher,
            current_publication_year=book.publication_year,
            current_page_count=book.page_count,
        )

        adapter_results = []
        for adapter in self._strategy.get_adapter_order(self._adapters, context):
            try:
                data = await adapter.enrich(context)
                if data.fields:
                    adapter_results.append(data)
            except Exception as e:
                logger.warning(f"Adapter {adapter.source_name} failed: {e}")

        merged = self._strategy.merge_data(context, adapter_results)

        changes = []
        update_data = {}

        for field, new_value in merged.items():
            current_value = getattr(book, field.value, None)
            if self._strategy.should_enrich_field(field, current_value, new_value, 0.8):
                update_data[field.value] = new_value
                changes.append(f"{field.value}: {len(str(current_value)) if current_value else 0} → {len(str(new_value))} chars")

        if update_data:
            for key, value in update_data.items():
                setattr(book, key, value)
            await self._db.commit()
            await self._db.refresh(book)

            return EnrichmentResult(
                book_id=book_id,
                status="enriched",
                changes=changes,
                sources_used=[r.source for r in adapter_results]
            )

        return EnrichmentResult(
            book_id=book_id,
            status="skipped"
        )

    async def enrich_multiple(self, book_ids: List[UUID]) -> List[EnrichmentResult]:
        results = []
        for book_id in book_ids:
            result = await self.enrich_book(book_id)
            results.append(result)
        return results
