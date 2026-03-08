from typing import List
from pydantic import BaseModel
from openai import AsyncOpenAI
from tenacity import retry, wait_exponential, stop_after_attempt
from src.config import settings
from src.services.ai.vector_service import VectorService
from src.core.exceptions import ShareBookException


wait = wait_exponential(multiplier=1, min=1, max=10)
stop = stop_after_attempt(3)

class Source(BaseModel):
    title: str
    author: str
    similarity_score: float
    content: str


class AIResponse(BaseModel):
    answer: str
    sources: List[Source]


class AIServiceException(ShareBookException):
    status_code = 503

    def __init__(self, message: str = "AI service error"):
        super().__init__(message=message, code="AI_SERVICE_ERROR")


class AIService:
    SYSTEM_PROMPT = """Jesteś kompetentnym i przyjaznym bibliotekarzem w systemie ShareBook.
    Twoim zadaniem jest pomagać użytkownikom znaleźć odpowiednie książki i odpowiadać na pytania o dostępne pozycje.
    
    Oto kontekst z katalogu biblioteki (najbardziej trafne pozycje):
    {context}
    
    Na podstawie powyższego kontekstu, odpowiedz na pytanie użytkownika.
    Bądź dokładny, merytoryczny i pomocny.
    Jeśli nie znasz odpowiedzi na podstawie dostarczonego kontekstu, szczerze to przyznaj.
    Nie wymyślaj informacji o książkach, których nie ma w kontekście.
    """
    
    def __init__(self, vector_service: VectorService):
        self._vector_service = vector_service
        self._client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self._model = settings.OPENAI_CHAT_MODEL
    
    @retry(wait=wait, stop=stop, reraise=True)
    async def get_recommendation(self, user_query: str) -> AIResponse:
        try:
            similar_chunks = await self._vector_service.search_similar(query=user_query, top_k=settings.AI_MAX_CONTEXT_CHUNKS)
            
            if not similar_chunks:
                return AIResponse(answer="Niestety, nie znalazłem książek pasujących do Twojego zapytania w naszym katalogu.", sources=[])
            
            context_parts = []
            sources = []
            
            for chunk, distance in similar_chunks:
                similarity = 1 - distance
                
                context_parts.append(
                    f"Książka: {chunk.book_title}\n"
                    f"Autor: {chunk.book_author}\n"
                    f"Fragment: {chunk.content[:500]}..."
                )
                sources.append(Source(
                    title=chunk.book_title,
                    author=chunk.book_author or "",
                    similarity_score=round(similarity, 3),
                    content=chunk.content[:200]
                ))
            
            context = "\n\n---\n\n".join(context_parts)
            
            messages = [
                {
                    "role": "system", 
                    "content": self.SYSTEM_PROMPT.format(context=context)
                },
                {"role": "user", "content": user_query}
            ]
            response = await self._client.chat.completions.create(
                model=self._model,
                messages=messages,
                temperature=0.7,
                max_tokens=settings.AI_MAX_TOKENS
            )
            
            answer = response.choices[0].message.content
            
            return AIResponse(
                answer=answer,
                sources=sources
            )
            
        except Exception as e:
            error_msg = str(e).lower()
            if "rate limit" in error_msg or "429" in error_msg:
                raise AIServiceException("AI service temporarily unavailable due to rate limiting. Please try again later.")
            elif "quota" in error_msg:
                raise AIServiceException("AI service quota exceeded. Please contact administrator.")
            elif "api key" in error_msg or "authentication" in error_msg:
                raise AIServiceException("AI service configuration error.")
            else:
                raise AIServiceException(f"AI service error: {str(e)}")
