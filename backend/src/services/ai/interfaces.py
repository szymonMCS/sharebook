from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Optional
from uuid import UUID
from database.models import BookChunk


@dataclass
class Chunk:
    headline: str
    summary: str
    original_text: str


@dataclass
class ChunkingResult:
    chunks: List[Chunk]
    strategy_used: str
    total_chars: int


class IChunkingStrategy(ABC):
    @abstractmethod
    async def chunk_text(self, title: str, author: str, description: str) -> ChunkingResult:
        pass
    @abstractmethod
    def supports(self, text_length: int) -> bool:
        pass


class IEmbeddingService(ABC):
    @abstractmethod
    async def generate_embedding(self, text: str) -> List[float]:
        pass
    @abstractmethod
    async def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        pass
    @abstractmethod
    def get_dimension(self) -> int:
        pass


class IVectorSearchService(ABC):
    @abstractmethod
    async def search_similar(self, query_embedding: List[float], limit: int = 3, book_id: Optional[UUID] = None) -> List[BookChunk]:
        pass
    @abstractmethod
    async def search_by_text(self, query: str, limit: int = 3, book_id: Optional[UUID] = None) -> List[BookChunk]:
        pass
    @abstractmethod
    async def get_stats(self) -> dict:
        pass
