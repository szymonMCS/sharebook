import logging
import asyncio
import re
import traceback
from dataclasses import dataclass
from typing import Any, Optional
from concurrent.futures import ThreadPoolExecutor
from src.config import settings
from .agent import BookSearchAgent

logger = logging.getLogger(__name__)


@dataclass
class BookSearchResult:
    success: bool
    data: dict[str, Any] | None = None
    results: list[dict[str, Any]] | None = None
    source: str = ""
    confidence: float = 0.0
    error: str | None = None


class UnifiedBookSearch:
    def __init__(self, openai_api_key: Optional[str] = None):
        self._api_key = openai_api_key or settings.OPENAI_API_KEY
        self._agent: Optional[BookSearchAgent] = None
        self._logger = logging.getLogger(self.__class__.__name__)
        self._executor = ThreadPoolExecutor(max_workers=3)
        
        if self._api_key:
            try:
                self._agent = BookSearchAgent(openai_api_key=self._api_key)
                self._logger.info("BookSearchAgent zainicjalizowany")
            except Exception as e:
                self._logger.error(f"Błąd inicjalizacji BookSearchAgent: {e}")
        else:
            self._logger.warning("OPENAI_API_KEY nie ustawiony!")

    async def search_by_isbn(self, isbn: str) -> BookSearchResult:
        if not self._agent:
            return BookSearchResult(
                success=False,
                error="OpenAI API key not configured",
                source="openai_web_search"
            )
        try:
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(self._executor, self._agent.search, isbn)
            if result.error:
                return BookSearchResult(
                    success=False,
                    error=result.error,
                    source="openai_web_search"
                )
            return BookSearchResult(
                success=True,
                data=result.__dict__,
                source="openai_web_search",
                confidence=result.confidence
            )
        except Exception as e:
            self._logger.error(traceback.format_exc())
            return BookSearchResult(
                success=False,
                error=f"Search error: {str(e)}",
                source="openai_web_search"
            )

    async def search_by_title(self, title: str, author: Optional[str] = None) -> BookSearchResult:
        query = title
        if author:
            query = f"{title} by {author}"
        if not self._agent:
            return BookSearchResult(
                success=False,
                error="OpenAI API key not configured",
                source="openai_web_search"
            )
        try:
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(self._executor, self._agent.search, query)
            if result.error:
                return BookSearchResult(
                    success=False,
                    error=result.error,
                    source="openai_web_search"
                )
            return BookSearchResult(
                success=True,
                results=[result.__dict__],
                source="openai_web_search",
                confidence=result.confidence
            )
        except Exception as e:
            self._logger.error(traceback.format_exc())
            return BookSearchResult(
                success=False,
                error=f"Search error: {str(e)}",
                source="openai_web_search"
            )

    async def close(self) -> None:
        self._executor.shutdown(wait=False)

    async def __aenter__(self) -> "UnifiedBookSearch":
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        await self.close()

def _is_isbn(query: str) -> bool:
    cleaned = re.sub(r'[\s\-]', '', query)
    return cleaned.isdigit() and len(cleaned) in [10, 13]

async def search_book(query: str, api_key: Optional[str] = None) -> dict[str, Any]:
    async with UnifiedBookSearch(openai_api_key=api_key) as search:
        result = await search.search_by_isbn(query) if _is_isbn(query) else await search.search_by_title(query)
        return result.data if result.success else {"error": result.error}
