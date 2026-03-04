import logging
from uuid import UUID
from typing import List, Dict, Optional
from dataclasses import dataclass, field
from openai import AsyncOpenAI
from database.models import BookChunk
from src.config import settings
from .vector_service import VectorService

logger = logging.getLogger(__name__)


@dataclass
class ChatMessage:
    role: str 
    content: str

@dataclass
class ChatContext:
    history: List[ChatMessage] = field(default_factory=list)
    relevant_chunks: List[BookChunk] = field(default_factory=list)
    user_id: Optional[UUID] = None


class AIService:
    SYSTEM_PROMPT = """Jesteś asystentem platformy ShareBook - systemu wymiany książek.

TWOJE ZADANIA:
1. Odpowiadaj na pytania o książki dostępne w systemie
2. Pomagaj znaleźć książki na podstawie opisów
3. Odpowiadaj na pytania o zasady wypożyczeń
4. Bądź pomocny, konkretny i przyjazny

REGUŁY:
- Odpowiadaj tylko na podstawie dostarczonego kontekstu (książki w sekcji KSIĄŻKI)
- Jeśli nie znasz odpowiedzi, przyznaj się: "Nie mam wystarczających informacji..."
- Nie wymyślaj książek których nie ma w kontekście
- Możesz polecać książki na podstawie podobieństwa tematycznego
- Odpowiadaj po polsku, chyba że użytkownik zapyta w innym języku

Kontekst zawiera fragmenty książek przetworzone przez Smart Chunking (z nagłówkami i podsumowaniami)."""

    def __init__(self, vector_service: VectorService):
        self._vector = vector_service
        self._openai = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self._max_chunks = settings.AI_MAX_CONTEXT_CHUNKS
        self._max_history = settings.AI_MAX_HISTORY_MESSAGES
        self._chat_model = settings.OPENAI_CHAT_MODEL
    
    def _build_prompt(self, user_message: str, context: ChatContext) -> List[Dict[str, str]]:
        messages = [{"role": "system", "content": self.SYSTEM_PROMPT}]
        
        if context.relevant_chunks:
            context_text = "DOSTĘPNE KSIĄŻKI W SYSTEMIE:\n\n"
            for i, chunk in enumerate(context.relevant_chunks, 1):
                context_text += f"{i}. {chunk.book_title}\n"
                context_text += f"   Fragment: {chunk.content[:300]}...\n\n"
            
            messages.append({"role": "system", "content": f"Fragmenty książek:\n\n{context_text}"})
        
        for msg in context.history[-self._max_history:]:
            messages.append({"role": msg.role, "content": msg.content})
        
        messages.append({"role": "user", "content": user_message})
        return messages
    
    async def chat(self, message: str, context: Optional[ChatContext] = None, book_id: Optional[UUID] = None) -> str:
        if context is None:
            context = ChatContext()
        
        try:
            chunks = await self._vector.search_similar(query=message, limit=self._max_chunks, book_id=book_id)
            context.relevant_chunks = chunks
            messages = self._build_prompt(message, context)
            response = await self._openai.chat.completions.create(
                model=self._chat_model,
                messages=messages,
                temperature=0.7,
                max_tokens=500
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"AI chat error: {e}")
            return "Przepraszam, wystąpił błąd. Spróbuj ponownie."
    
    async def get_recommendation(self, query: str) -> dict:
        answer = await self.chat(query)
        sources = []
        
        return {
            "answer": answer,
            "sources": sources,
            "model_used": self._chat_model
        }
    
    async def get_health_status(self) -> Dict:
        try:
            await self._openai.embeddings.create(
                model=settings.OPENAI_EMBEDDING_MODEL, input="test"
            )
            openai_status = "ok"
        except Exception as e:
            openai_status = f"error: {str(e)}"
        
        indexed_count = await self._vector.get_indexed_books_count()
        
        return {
            "openai_connection": openai_status,
            "indexed_books": indexed_count,
            "embedding_model": settings.OPENAI_EMBEDDING_MODEL,
            "chat_model": self._chat_model,
            "chunking_type": "smart (LLM)"
        }
