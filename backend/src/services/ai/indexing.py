import logging
from uuid import UUID
from typing import List
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession
from database.models import Book, BookChunk
from src.services.ai.interfaces import IChunkingStrategy, IEmbeddingService
from src.services.ai.chunking import SimpleChunkingStrategy

logger = logging.getLogger(__name__)


class BookIndexingService:
    def __init__(self, db: AsyncSession, embedding_service: IEmbeddingService, chunking_strategy: IChunkingStrategy = None):
        self._db = db
        self._embedding = embedding_service
        self._chunking = chunking_strategy or SimpleChunkingStrategy()

    async def index_book(self, book_id: UUID, title: str, author: str, description: str) -> int:
        if not description:
            logger.warning(f"Book {book_id} has no description to index")
            return 0

        await self._db.execute(text("DELETE FROM book_chunks WHERE book_id = :book_id"), {"book_id": str(book_id)})

        result = await self._chunking.chunk_text(title, author, description)

        for index, chunk in enumerate(result.chunks):
            text_for_embedding = f"{chunk.headline}\n{chunk.summary}\n{chunk.original_text}"
            embedding = await self._embedding.generate_embedding(text_for_embedding)

            book_chunk = BookChunk(
                book_id=book_id,
                book_title=title,
                book_author=author,
                content=chunk.original_text,
                embedding=embedding,
                chunk_index=index
            )
            self._db.add(book_chunk)

        await self._db.commit()
        logger.info(f"Indexed book '{title}': {len(result.chunks)} chunks ({result.strategy_used})")
        return len(result.chunks)

    async def index_all_books(self) -> dict:
        result = await self._db.execute(select(Book).where(Book.description.is_not(None)))
        books = result.scalars().all()

        indexed = 0
        errors = []
        total_chunks = 0

        for book in books:
            try:
                chunks = await self.index_book(
                    book_id=book.id,
                    title=book.title,
                    author=book.author or "",
                    description=book.description or ""
                )
                total_chunks += chunks
                indexed += 1
            except Exception as e:
                logger.error(f"Failed to index book {book.id}: {e}")
                errors.append(str(book.id))
        return {
            "total_books": len(books),
            "indexed_books": indexed,
            "total_chunks": total_chunks,
            "errors": errors
        }

    async def delete_book_index(self, book_id: UUID) -> bool:
        await self._db.execute(text("DELETE FROM book_chunks WHERE book_id = :book_id"), {"book_id": str(book_id)})
        await self._db.commit()
        return True
