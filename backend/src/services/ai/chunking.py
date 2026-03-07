import logging
from typing import List
from openai import AsyncOpenAI
from pydantic import BaseModel
from src.config import settings
from src.services.ai.interfaces import IChunkingStrategy, Chunk, ChunkingResult

logger = logging.getLogger(__name__)


class _ChunkModel(BaseModel):
    headline: str
    summary: str
    original_text: str


class _ChunksModel(BaseModel):
    chunks: List[_ChunkModel]


class SmartChunkingStrategy(IChunkingStrategy):
    def __init__(self, openai_client: AsyncOpenAI = None, model: str = None):
        self._client = openai_client or AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self._model = model or settings.OPENAI_CHAT_MODEL

    def supports(self, text_length: int) -> bool:
        return text_length >= 100

    def _create_prompt(self, title: str, author: str, description: str) -> str:
        estimated = (len(description) // 800) + 1
        return f"""Twoim zadaniem jest podzielenie opisu książki na nakładające się fragmenty (chunki) do Bazy Wiedzy AI.

Książka: "{title}"
Autor: {author}

ZASADY PODZIAŁU:
1. Podziel tekst na {estimated}-{estimated + 2} fragmenty (chunki)
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

    async def chunk_text(self, title: str, author: str, description: str) -> ChunkingResult:
        try:
            prompt = self._create_prompt(title, author, description)
            response = await self._client.chat.completions.create(
                model=self._model,
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"},
                temperature=0.3,
                max_tokens=2000
            )

            content = response.choices[0].message.content
            data = _ChunksModel.model_validate_json(content)
            chunks = [Chunk(headline=c.headline, summary=c.summary, original_text=c.original_text) for c in data.chunks]

            logger.info(f"Smart chunking created {len(chunks)} chunks for '{title}'")

            return ChunkingResult(
                chunks=chunks,
                strategy_used="smart",
                total_chars=len(description)
            )

        except Exception as e:
            logger.error(f"Smart chunking failed for '{title}': {e}")
            raise


class SimpleChunkingStrategy(IChunkingStrategy):
    def __init__(self, chunk_size: int = 1000, overlap: int = 200):
        self._chunk_size = chunk_size
        self._overlap = overlap

    def supports(self, text_length: int) -> bool:
        return True

    async def chunk_text(self, title: str, author: str, description: str) -> ChunkingResult:
        if len(description) <= self._chunk_size:
            return ChunkingResult(
                chunks=[Chunk(
                    headline=f"{title} - opis",
                    summary=description[:200] + "..." if len(description) > 200 else description,
                    original_text=description
                )],
                strategy_used="simple",
                total_chars=len(description)
            )

        chunks = []
        start = 0
        index = 0

        while start < len(description):
            end = start + self._chunk_size

            if end < len(description):
                while end > start and description[end] not in [' ', '.', '!', '?', '\n']:
                    end -= 1

            chunk_text = description[start:end].strip()
            if chunk_text:
                chunks.append(Chunk(
                    headline=f"{title} - fragment {index + 1}",
                    summary=chunk_text[:150] + "..." if len(chunk_text) > 150 else chunk_text,
                    original_text=chunk_text
                ))
                index += 1

            start = end - self._overlap if end < len(description) else end

        return ChunkingResult(
            chunks=chunks,
            strategy_used="simple",
            total_chars=len(description)
        )
