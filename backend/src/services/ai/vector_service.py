import uuid
from typing import List, Tuple
from pathlib import Path
import aiofiles
from openai import AsyncOpenAI
from sqlalchemy import select, delete, text
from sqlalchemy.ext.asyncio import AsyncSession
from tenacity import retry, wait_exponential, stop_after_attempt
from src.config import settings
from database.models import BookChunk, Book

wait = wait_exponential(multiplier=1, min=1, max=10)
stop = stop_after_attempt(3)


class VectorService:
    def __init__(self, vector_db: AsyncSession):
        self._db = vector_db
        self._client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self._embedding_model = settings.OPENAI_EMBEDDING_MODEL
        self._chunk_size = settings.CHUNK_SIZE
        self._chunk_overlap = settings.CHUNK_OVERLAP
    
    def _chunk_text(self, text: str, book_title: str, book_author: str) -> List[str]:
        chunks = []
        prefix = f"Tytuł: {book_title}\nAutor: {book_author}\n\n"
        
        start = 0
        text_len = len(text)
        
        while start < text_len:
            end = min(start + self._chunk_size, text_len)
            
            if end < text_len:
                for i in range(min(100, end - start)):
                    if text[end - i - 1] in ".!?\n":
                        end = end - i
                        break
            
            chunk_content = prefix + text[start:end].strip()
            if chunk_content:
                chunks.append(chunk_content)
            
            start = end - self._chunk_overlap if end < text_len else end
        return chunks
    
    @retry(wait=wait, stop=stop, reraise=True)
    async def _generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        response = await self._client.embeddings.create(model=self._embedding_model, input=texts)
        return [item.embedding for item in response.data]
    
    async def upsert_book_chunks(self, book_id: uuid.UUID, book_title: str, book_author: str, description: str | None) -> int:
        await self._db.execute(delete(BookChunk).where(BookChunk.book_id == book_id))
        await self._db.commit()
        
        if not description:
            return 0
        
        chunks = self._chunk_text(description, book_title, book_author)
        
        if not chunks:
            return 0
        
        embeddings = await self._generate_embeddings(chunks)
        
        for idx, (chunk_text, embedding) in enumerate(zip(chunks, embeddings)):
            book_chunk = BookChunk(
                book_id=book_id,
                book_title=book_title,
                book_author=book_author,
                content=chunk_text,
                embedding=embedding,
                chunk_index=idx
            )
            self._db.add(book_chunk)
        
        await self._db.commit()
        return len(chunks)
    
    async def delete_book_chunks(self, book_id: uuid.UUID) -> None:
        await self._db.execute(delete(BookChunk).where(BookChunk.book_id == book_id))
        await self._db.commit()
    
    @retry(wait=wait, stop=stop, reraise=True)
    async def search_similar(self, query: str, top_k: int = 3) -> List[Tuple[BookChunk, float]]:
        response = await self._client.embeddings.create(model=self._embedding_model, input=[query])
        query_embedding = response.data[0].embedding
        
        stmt = select(BookChunk, BookChunk.embedding.cosine_distance(query_embedding).label("distance")).order_by(
            BookChunk.embedding.cosine_distance(query_embedding)).limit(top_k)
        
        result = await self._db.execute(stmt)
        rows = result.all()
        return [(row[0], float(row[1])) for row in rows]
    
    async def process_markdown_file(self, file_path: str | None = None) -> int:
        path = Path(file_path or settings.KNOWLEDGE_BASE_PATH)
        
        if not path.exists():
            return 0
        
        async with aiofiles.open(path, "r", encoding="utf-8") as f:
            content = await f.read()
        
        sections = content.split("\n### ")
        chunks = []
        
        for section in sections[1:]: 
            lines = section.strip().split("\n")
            title = lines[0]
            body = "\n".join(lines[1:])
            chunk_text = f"Tytuł: {title}\n{body}"
            chunks.append(chunk_text)
        
        if not chunks:
            return 0
        
        await self._db.execute(delete(BookChunk))
        await self._db.commit()
        
        embeddings = await self._generate_embeddings(chunks)
        
        for chunk_text, embedding in zip(chunks, embeddings):
            lines = chunk_text.split("\n")
            title_line = lines[0].replace("Tytuł: ", "")
            
            book_chunk = BookChunk(
                book_id=uuid.uuid4(), 
                book_title=title_line,
                book_author="Unknown",
                content=chunk_text,
                embedding=embedding,
                chunk_index=0
            )
            self._db.add(book_chunk)
        
        await self._db.commit()
        return len(chunks)
    
    async def create_hnsw_index(self) -> None:
        await self._db.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_book_chunks_embedding_hnsw 
            ON book_chunks 
            USING hnsw (embedding vector_cosine_ops)
            WITH (m = 16, ef_construction = 64)
        """))
        await self._db.commit()
    
    async def sync_all_books(self) -> int:
        result = await self._db.execute(select(Book))
        books = result.scalars().all()
        
        count = 0
        for book in books:
            chunks = await self.upsert_book_chunks(
                book_id=book.id,
                book_title=book.title,
                book_author=book.author or "",
                description=book.description
            )
            if chunks > 0:
                count += 1
        
        return count
