import logging
from uuid import UUID
from typing import List, Optional
from openai import AsyncOpenAI
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession
from database.models import BookChunk
from src.config import settings
from .chunking_models import Chunk, Chunks

logger = logging.getLogger(__name__)


class VectorService:
    def __init__(self, db: AsyncSession):
        self._db = db
        self._openai = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self._chunking_model = settings.OPENAI_CHAT_MODEL  # gpt-4o-mini
    
    def _create_chunking_prompt(self, title: str, author: str, description: str) -> str:
        estimated_chunks = (len(description) // 800) + 1
        
        return f"""Twoim zadaniem jest podzielenie opisu książki na nakładające się fragmenty (chunki) do Bazy Wiedzy AI.

Książka: "{title}" 
Autor: {author}

Chatbot będzie wykorzystywał te fragmenty do odpowiadania na pytania użytkowników o książki dostępne w systemie ShareBook (platforma wymiany książek).

ZASADY PODZIAŁU:
1. Podziel tekst na {estimated_chunks}-{estimated_chunks + 2} fragmenty (chunki)
2. Każdy fragment powinien mieć 200-400 słów
3. Nakładanie (overlap) między fragmentami: około 25% lub ~50 słów
4. Nie pomijaj żadnych informacji - cała treść musi być uwzględniona
5. Dziel wg sensownych granic (akapity, rozdziały, tematy)

DLA KAŻDEGO FRAGMENTU podaj:
- headline: Krótki, konkretny nagłówek odpowiadający zapytaniu (np. "Fabuła kryminału", "Główny bohater", "Recenzja pozytywna")
- summary: 2-3 zdania podsumowujące treść fragmentu
- original_text: Dokładny, oryginalny tekst fragmentu bez zmian

OPIS KSIĄŻKI DO PODZIAŁU:
{description}

Zwróć wynik jako JSON zgodnie ze schematem:
{{
  "chunks": [
    {{
      "headline": "...",
      "summary": "...",
      "original_text": "..."
    }}
  ]
}}"""

    async def _smart_chunk_text(self, title: str, author: str, description: str) -> List[Chunk]:
        if not description or len(description) < 100:
            # Za krótki tekst - jeden chunk
            return [Chunk(
                headline=f"{title} - {author}",
                summary=description[:200] + "..." if len(description) > 200 else description,
                original_text=description
            )]
        
        try:
            prompt = self._create_chunking_prompt(title, author, description)
            
            response = await self._openai.chat.completions.create(
                model=self._chunking_model,
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"},
                temperature=0.3,
                max_tokens=2000
            )
            
            content = response.choices[0].message.content
            chunks_data = Chunks.model_validate_json(content)
            
            logger.info(f"Smart chunking created {len(chunks_data.chunks)} chunks for '{title}'")
            return chunks_data.chunks
            
        except Exception as e:
            logger.warning(f"Smart chunking failed for '{title}', falling back to simple: {e}")
            return self._simple_chunk_fallback(title, author, description)
    
    def _simple_chunk_fallback(self, title: str, author: str, text: str, chunk_size: int = 1000, overlap: int = 200) -> List[Chunk]:
        """Prosty podział tekstu na chunki (fallback).
        Używany gdy LLM chunking zawiedzie lub dla krótkich tekstów.
        """
        if len(text) <= chunk_size:
            return [Chunk(
                headline=f"{title} - opis",
                summary=text[:200] + "..." if len(text) > 200 else text,
                original_text=text
            )]
        
        chunks = []
        start = 0
        index = 0
        
        while start < len(text):
            end = start + chunk_size
            
            # Nie przecinaj w środku słowa
            if end < len(text):
                while end > start and text[end] not in [' ', '.', '!', '?', '\n']:
                    end -= 1
            
            chunk_text = text[start:end].strip()
            if chunk_text:
                chunks.append(Chunk(
                    headline=f"{title} - fragment {index + 1}",
                    summary=chunk_text[:150] + "..." if len(chunk_text) > 150 else chunk_text,
                    original_text=chunk_text
                ))
                index += 1
            
            start = end - overlap if end < len(text) else end
        
        return chunks
    
    async def _generate_embedding(self, text: str) -> List[float]:
        try:
            response = await self._openai.embeddings.create(
                model=settings.OPENAI_EMBEDDING_MODEL,
                input=text[:8000]
            )
            return response.data[0].embedding
        except Exception as e:
            logger.error(f"Failed to generate embedding: {e}")
            raise
    
    async def search_similar(self, query: str, limit: int = 3,book_id: Optional[UUID] = None) -> List[BookChunk]:

        query_embedding = await self._generate_embedding(query)
        sql = """
            SELECT id, book_id, book_title, content, chunk_index, 
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
        
        chunks = []
        for row in rows:
            chunk = BookChunk(
                id=row[0],
                book_id=row[1],
                book_title=row[2],
                content=row[3],
                chunk_index=row[4]
            )
            chunks.append(chunk)
        
        logger.info(f"Found {len(chunks)} similar chunks for query: {query[:50]}...")
        return chunks
    
    async def index_book(self, book_id: UUID, title: str, author: str, description: str) -> int:
        if not description:
            logger.warning(f"Book {book_id} has no description to index")
            return 0
        
        await self._db.execute(
            text("DELETE FROM book_chunks WHERE book_id = :book_id"),
            {"book_id": str(book_id)}
        )
        
        chunks = await self._smart_chunk_text(title, author, description)
        
        for index, chunk in enumerate(chunks):
            text_for_embedding = f"{chunk.headline}\n{chunk.summary}\n{chunk.original_text}"
            embedding = await self._generate_embedding(text_for_embedding)
            
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
        logger.info(f"Indexed book '{title}': {len(chunks)} smart chunks")
        return len(chunks)
    
    async def get_indexed_books_count(self) -> int:
        result = await self._db.execute(
            select(text("COUNT(DISTINCT book_id)")).select_from(text("book_chunks"))
        )
        return result.scalar() or 0
    
    async def get_stats(self) -> dict:
        try:
            total_chunks = await self._db.execute(
                select(text("COUNT(*)")).select_from(text("book_chunks"))
            )
            total_books = await self._db.execute(
                select(text("COUNT(DISTINCT book_id)")).select_from(text("book_chunks"))
            )
            
            return {
                "total_books": total_books.scalar() or 0,
                "total_chunks": total_chunks.scalar() or 0,
                "status": "connected",
                "chunking_type": "smart (LLM)"
            }
        except Exception as e:
            return {
                "total_books": 0,
                "total_chunks": 0,
                "status": f"error: {str(e)}",
                "chunking_type": "unknown"
            }
    
    async def sync_all_books(self) -> dict:
        from database.models import Book
        
        result = await self._db.execute(
            select(Book).where(Book.description.is_not(None))
        )
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
