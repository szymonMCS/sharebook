import logging
from uuid import UUID
from typing import List
from database.models import Book, BookChunk
from database.interfaces import IBookChunkRepository, IBookRepository
from src.services.interfaces import IChunkingStrategy, IEmbeddingService
from src.services.ai.chunking import SimpleChunkingStrategy

logger = logging.getLogger(__name__)


class BookIndexingService:
    def __init__(
        self,
        book_repo: IBookRepository,
        chunk_repo: IBookChunkRepository,
        embedding_service: IEmbeddingService,
        chunking_strategy: IChunkingStrategy = None
    ):
        self._book_repo = book_repo
        self._chunk_repo = chunk_repo
        self._embedding = embedding_service
        self._chunking = chunking_strategy or SimpleChunkingStrategy()

    async def index_book(self, book_id: UUID, title: str, author: str, description: str) -> int:
        if not description:
            logger.warning(f"Book {book_id} has no description to index")
            return 0

        await self._chunk_repo.delete_by_book_id(book_id)

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
            await self._chunk_repo.add_chunk(book_chunk)

        await self._chunk_repo.commit()
        logger.info(f"Indexed book '{title}': {len(result.chunks)} chunks ({result.strategy_used})")
        return len(result.chunks)

    async def index_all_books(self) -> dict:
        books, _ = await self._book_repo.get_multi(limit=10000)
        
        indexed = 0
        errors = []
        total_chunks = 0

        for book in books:
            if not book.description:
                continue
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
        await self._chunk_repo.delete_by_book_id(book_id)
        await self._chunk_repo.commit()
        return True
