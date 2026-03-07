import logging
from typing import List, Optional
from uuid import UUID
from database.models import BookChunk
from database.interfaces import IBookChunkRepository
from src.services.interfaces import IVectorSearchService, IEmbeddingService

logger = logging.getLogger(__name__)


class PgVectorSearchService(IVectorSearchService):
    def __init__(self, chunk_repo: IBookChunkRepository, embedding_service: IEmbeddingService):
        self._chunk_repo = chunk_repo
        self._embedding = embedding_service

    async def search_similar(self, query_embedding: List[float], limit: int = 3, book_id: Optional[UUID] = None) -> List[BookChunk]:
        return await self._chunk_repo.search_similar(query_embedding, limit, book_id)

    async def search_by_text(self, query: str, limit: int = 3, book_id: Optional[UUID] = None) -> List[BookChunk]:
        embedding = await self._embedding.generate_embedding(query)
        return await self.search_similar(embedding, limit, book_id)

    async def get_stats(self) -> dict:
        return await self._chunk_repo.get_stats()
