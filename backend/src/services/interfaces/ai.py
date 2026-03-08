from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Optional, Tuple
from uuid import UUID
from database.models import BookChunk


class IVectorService(ABC):
    """Interface for vector service managing embeddings and similarity search.
    
    This is the new template-based interface for vector operations.
    """
    
    @abstractmethod
    async def upsert_book_chunks(
        self, 
        book_id: UUID, 
        book_title: str, 
        book_author: str, 
        description: Optional[str]
    ) -> int:
        """Create and store embeddings for a book. Returns number of chunks created."""
        pass
    
    @abstractmethod
    async def delete_book_chunks(self, book_id: UUID) -> None:
        """Delete all chunks for a book."""
        pass
    
    @abstractmethod
    async def search_similar(
        self, 
        query: str, 
        top_k: int = 3
    ) -> List[Tuple[BookChunk, float]]:
        """Search for similar chunks using vector similarity. Returns chunks with distance scores."""
        pass
    
    @abstractmethod
    async def process_markdown_file(self, file_path: Optional[str] = None) -> int:
        """Process markdown file and create embeddings. Returns number of chunks created."""
        pass
    
    @abstractmethod
    async def create_hnsw_index(self) -> None:
        """Create HNSW index for faster similarity search."""
        pass
    
    @abstractmethod
    async def sync_all_books(self) -> int:
        """Sync embeddings for all books in the catalog. Returns number of books processed."""
        pass


@dataclass
class Source:
    """Source book for AI response."""
    title: str
    author: str
    similarity_score: float
    content: str


@dataclass
class AIResponse:
    """Response from AI service."""
    answer: str
    sources: List[Source]


class IAIService(ABC):
    """Interface for AI service providing RAG-based recommendations.
    
    This is the new template-based interface for AI operations.
    """
    
    @abstractmethod
    async def get_recommendation(self, user_query: str) -> AIResponse:
        """Get book recommendation using RAG."""
        pass


class IMarkdownGeneratorService(ABC):
    """Interface for markdown generator service.
    
    Generates markdown catalog of books for RAG knowledge base.
    """
    
    @abstractmethod
    async def generate_catalog(self) -> str:
        """Generate markdown catalog of all books."""
        pass
    
    @abstractmethod
    async def save_to_file(self, content: str, path: Optional[str] = None) -> str:
        """Save markdown content to file. Returns file path."""
        pass
    
    @abstractmethod
    async def regenerate(self, path: Optional[str] = None) -> str:
        """Regenerate and save catalog. Returns file path."""
        pass
