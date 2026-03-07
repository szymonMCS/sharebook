import json
import logging
from typing import Any, Dict, List, Optional
from openai import AsyncOpenAI
from src.config import settings
from src.core.constants import PLACEHOLDER_TITLE
from src.services.interfaces import IEnrichmentAdapter, EnrichmentData, EnrichmentContext, EnrichmentField
from src.services.google_books_client import get_google_books_client

logger = logging.getLogger(__name__)


class GoogleBooksAdapter(IEnrichmentAdapter):
    SOURCE_NAME = "google_books"
    SUPPORTED_FIELDS = [
        EnrichmentField.TITLE,
        EnrichmentField.AUTHOR,
        EnrichmentField.DESCRIPTION,
        EnrichmentField.PUBLISHER,
        EnrichmentField.PUBLICATION_YEAR,
        EnrichmentField.PAGE_COUNT,
        EnrichmentField.GENRE,
        EnrichmentField.COVER_URL,
        EnrichmentField.LANGUAGE,
    ]

    def __init__(self, client=None):
        self._client = client or get_google_books_client()

    @property
    def source_name(self) -> str:
        return self.SOURCE_NAME

    @property
    def supported_fields(self) -> List[EnrichmentField]:
        return self.SUPPORTED_FIELDS

    def is_available(self) -> bool:
        return True

    async def enrich(self, context: EnrichmentContext) -> EnrichmentData:
        if not context.isbn:
            return EnrichmentData(source=self.SOURCE_NAME)

        try:
            google_data = await self._client.fetch_by_isbn(context.isbn)
            if not google_data:
                return EnrichmentData(source=self.SOURCE_NAME)

            fields = {}

            if google_data.get("title"):
                fields[EnrichmentField.TITLE] = google_data["title"]
            if google_data.get("authors"):
                fields[EnrichmentField.AUTHOR] = ", ".join(google_data["authors"])
            if google_data.get("description"):
                fields[EnrichmentField.DESCRIPTION] = google_data["description"]
            if google_data.get("publisher"):
                fields[EnrichmentField.PUBLISHER] = google_data["publisher"]
            if google_data.get("publication_year"):
                fields[EnrichmentField.PUBLICATION_YEAR] = google_data["publication_year"]
            if google_data.get("page_count"):
                fields[EnrichmentField.PAGE_COUNT] = google_data["page_count"]
            if google_data.get("genre"):
                fields[EnrichmentField.GENRE] = google_data["genre"]
            if google_data.get("cover_url"):
                fields[EnrichmentField.COVER_URL] = google_data["cover_url"]

            return EnrichmentData(
                source=self.SOURCE_NAME,
                fields=fields,
                confidence=0.9,
                raw_data=google_data
            )
        except Exception as e:
            logger.warning(f"Google Books failed for {context.isbn}: {e}")
            return EnrichmentData(source=self.SOURCE_NAME)


class OpenAIAdapter(IEnrichmentAdapter):
    SOURCE_NAME = "openai"
    SUPPORTED_FIELDS = [
        EnrichmentField.DESCRIPTION,
        EnrichmentField.TITLE,
        EnrichmentField.AUTHOR,
    ]

    def __init__(self, client: AsyncOpenAI = None, model: str = None):
        self._client = client or AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self._model = model or settings.OPENAI_CHAT_MODEL

    @property
    def source_name(self) -> str:
        return self.SOURCE_NAME

    @property
    def supported_fields(self) -> List[EnrichmentField]:
        return self.SUPPORTED_FIELDS

    def is_available(self) -> bool:
        return settings.OPENAI_API_KEY is not None

    async def enrich(self, context: EnrichmentContext) -> EnrichmentData:
        fields = {}

        current_desc_len = len(context.current_description) if context.current_description else 0
        if current_desc_len < 500:
            description = await self._generate_description(context)
            if description and len(description) > current_desc_len:
                fields[EnrichmentField.DESCRIPTION] = description

        if context.current_title in [PLACEHOLDER_TITLE, "", None] and context.isbn:
            title, author = await self._generate_title_author(context.isbn)
            if title:
                fields[EnrichmentField.TITLE] = title
            if author:
                fields[EnrichmentField.AUTHOR] = author

        return EnrichmentData(
            source=self.SOURCE_NAME,
            fields=fields,
            confidence=0.7,
        )

    async def _generate_description(self, context: EnrichmentContext) -> Optional[str]:
        context_parts = []
        if context.current_title and context.current_title != PLACEHOLDER_TITLE:
            context_parts.append(f"Tytuł: {context.current_title}")
        if context.current_author:
            context_parts.append(f"Autor: {context.current_author}")
        if context.isbn:
            context_parts.append(f"ISBN: {context.isbn}")
        if context.current_genre:
            context_parts.append(f"Gatunek: {context.current_genre}")
        if context.current_description:
            context_parts.append(f"Istniejący opis: {context.current_description[:300]}")

        prompt = f"""Jesteś profesjonalnym bibliotekarzem. Napisz opis książki w języku polskim.

DANE KSIĄŻKI:
{'\n'.join(context_parts)}

ZASADY:
1. Opis powinien być bogaty i szczegółowy (800-1200 znaków)
2. Napisz profesjonalnym, ale przystępnym językiem
3. Zawieraj: o czym jest książka, dla kogo jest przeznaczona, dlaczego warto przeczytać
4. Nie wymyślaj faktów - użyj tylko podanego kontekstu

Napisz TYLKO opis, bez nagłówków, bez cudzysłowów na początku i końca."""

        try:
            response = await self._client.chat.completions.create(
                model=self._model,
                messages=[
                    {"role": "system", "content": "Jesteś bibliotekarzem piszącym opisy książek."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=800,
            )

            description = response.choices[0].message.content.strip()
            description = description.strip('"\'')
            if description.startswith("Opis:"):
                description = description[5:].strip()

            if len(description) < 200:
                return None

            return description
        except Exception as e:
            logger.error(f"OpenAI description generation failed: {e}")
            return None

    async def _generate_title_author(self, isbn: str) -> tuple[Optional[str], Optional[str]]:
        prompt = f"""Podaj tytuł i autora książki o ISBN: {isbn}

Odpowiedz w formacie JSON z polami:
- title: string (tytuł książki lub null jeśli nieznany)
- author: string (autor książki lub null jeśli nieznany)
- known: boolean (true jeśli znasz ten ISBN, false jeśli nie)"""

        try:
            response = await self._client.chat.completions.create(
                model=self._model,
                messages=[
                    {"role": "system", "content": "Jesteś bibliotekarzem z dostępem do katalogu ISBN. Odpowiadaj wyłącznie w formacie JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=200,
                response_format={"type": "json_object"}
            )

            content = response.choices[0].message.content.strip()
            data = json.loads(content)
            title = data.get("title")
            author = data.get("author")
            known = data.get("known", True)

            if not known or title == "Nieznane":
                return None, None

            return title, author
        except Exception as e:
            logger.error(f"OpenAI title/author generation failed: {e}")
            return None, None
