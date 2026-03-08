import json
import logging
from typing import Optional
from openai import AsyncOpenAI
from src.config import settings
from .query_builder import QueryBuilder, SearchQuery
from .search_executor import SearchExecutor
from .result_formatter import ResultFormatter, BookData

logger = logging.getLogger(__name__)


class BookSearchAgent:
    def __init__(self, openai_api_key: Optional[str] = None):
        api_key = openai_api_key or settings.OPENAI_API_KEY
        self.client = AsyncOpenAI(api_key=api_key)
        self.model = settings.OPENAI_CHAT_MODEL
        self._logger = logging.getLogger(self.__class__.__name__)
        self.query_builder = QueryBuilder()
        self.search_executor = SearchExecutor(timeout=5.0)
        self.result_formatter = ResultFormatter()
    
    async def search(self, query: str) -> BookData:
        self._logger.info(f"[AI Search] START: '{query}'")
        search_query = self.query_builder.build(query)
        if not search_query:
            return self.result_formatter.format_error("Empty query")
        self._logger.info(f"[AI Search] Type: {'ISBN' if search_query.is_isbn else 'text'}")
        try:
            response = await self.client.responses.create(
                model=self.model,
                tools=[{"type": "web_search"}],
                input=[
                    {"role": "system", "content": self.query_builder.get_system_prompt()},
                    {"role": "user", "content": self.query_builder.build_prompt(search_query)}
                ]
            )
            content = response.output_text
            self._logger.debug(f"[AI Search] Response: {content[:500]}...")
            llm_data = self._extract_json(content)
            if not llm_data:
                return self.result_formatter.format_error("No valid JSON in response")
            if llm_data.get("error"):
                return self.result_formatter.format_error(llm_data["error"])
    
            cover_url = await self._get_cover_url(llm_data, search_query.normalized_isbn)
            
            self._logger.info(f"[AI Search] END")
            return self.result_formatter.format(llm_data, cover_url)
            
        except Exception as e:
            self._logger.error(f"[AI Search] Error: {e}")
            return self.result_formatter.format_error(f"Search failed: {e}")
    
    def _extract_json(self, content: str) -> Optional[dict]:
        try:
            if "```json" in content:
                json_text = content.split("```json")[1].split("```")[0].strip()
                return json.loads(json_text)
            
            start = content.find("{")
            end = content.rfind("}")
            if start != -1 and end != -1 and start < end:
                return json.loads(content[start:end+1])
            
            return json.loads(content)
        except (json.JSONDecodeError, IndexError) as e:
            self._logger.error(f"JSON extraction failed: {e}")
            return None
    
    async def _get_cover_url(self, llm_data: dict, query_isbn: Optional[str]) -> Optional[str]:
        isbn = llm_data.get("isbn_13") or llm_data.get("isbn_10") or query_isbn
        if not isbn:
            return None
        self._logger.info(f"[AI Search] Looking for cover: {isbn}")
        try:
            result = await self.search_executor.get_cover_from_openlibrary(isbn)
            if result.url:
                return result.url
        except Exception as e:
            self._logger.debug(f"OpenLibrary error: {e}")
        
        try:
            result = await self.search_executor.get_cover_from_google(isbn)
            if result.url:
                return result.url
        except Exception as e:
            self._logger.debug(f"Google Books error: {e}")
        
        self._logger.warning("[AI Search] No cover found")
        return None
