import logging
from typing import List, Optional
from uuid import UUID
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from database.models import BookChunk
from src.services.ai.interfaces import IVectorSearchService, IEmbeddingService

logger = logging.getLogger(__name__)


class PgVectorSearchService(IVectorSearchService):
    def __init__(self, db: AsyncSession, embedding_service: IEmbeddingService):
        self._db = db
        self._embedding = embedding_service

    async def search_similar(self, query_embedding: List[float], limit: int = 3, book_id: Optional[UUID] = None) -> List[BookChunk]:
        sql = """
            SELECT id, book_id, book_title, book_author, content, chunk_index,
                   embedding <=> :embedding as distance
            FROM book_chunks
            WHERE embedding IS NOT NULL
        """
        params = {"embedding": str(query_embedding)}

        if book_id:
            sql += " AND book_id = :book_id"
            params["book_id"] = str(book_id)

        sql += " ORDER BY embedding <=> :embedding LIMIT :limit"
        params["limit"] = limit

        result = await self._db.execute(text(sql), params)
        rows = result.fetchall()

        return [
            BookChunk(
                id=row[0],
                book_id=row[1],
                book_title=row[2],
                book_author=row[3],
                content=row[4],
                chunk_index=row[5]
            )
            for row in rows
        ]

    async def search_by_text(self, query: str, limit: int = 3, book_id: Optional[UUID] = None) -> List[BookChunk]:
        embedding = await self._embedding.generate_embedding(query)
        return await self.search_similar(embedding, limit, book_id)

    async def get_stats(self) -> dict:
        try:
            total = await self._db.execute(text("SELECT COUNT(*) FROM book_chunks"))
            books = await self._db.execute(text("SELECT COUNT(DISTINCT book_id) FROM book_chunks"))
            return {
                "total_chunks": total.scalar() or 0,
                "total_books": books.scalar() or 0,
                "status": "connected"
            }
        except Exception as e:
            return {
                "total_chunks": 0,
                "total_books": 0,
                "status": f"error: {str(e)}"
            }
