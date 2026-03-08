import logging
from typing import Any, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class BookData:
    full_title: str
    short_description: str
    cover_image_url: Optional[str]
    author: str
    isbn_13: Optional[str]
    isbn_10: Optional[str]
    confidence: float
    error: Optional[str] = None
    page_count: Optional[int] = None
    publication_year: Optional[int] = None
    genre: Optional[str] = None
    language: Optional[str] = None
    publisher: Optional[str] = None


class ResultFormatter:
    @staticmethod
    def parse_int(value: Any) -> Optional[int]:
        if value is None or value == "":
            return None
        try:
            return int(value)
        except (ValueError, TypeError):
            return None

    @staticmethod
    def calculate_confidence(data: dict) -> float:
        base_confidence = data.get("confidence", 0.0)
        required_fields = ["full_title", "author", "short_description"]
        optional_fields = ["isbn_13", "isbn_10", "page_count", "publication_year", "genre"]
        required_score = sum(1 for f in required_fields if data.get(f)) / len(required_fields)
        optional_score = sum(1 for f in optional_fields if data.get(f)) / len(optional_fields)
        final_confidence = (base_confidence * 0.5) + (required_score * 0.3) + (optional_score * 0.2)
        return min(1.0, max(0.0, final_confidence))

    def format(self, llm_data: dict, cover_url: Optional[str]) -> BookData:
        confidence = self.calculate_confidence(llm_data)
        logger.info(f"[Formatter] Title: {llm_data.get('full_title', 'N/A')}")
        logger.info(f"[Formatter] Author: {llm_data.get('author', 'N/A')}")
        logger.info(f"[Formatter] Genre: {llm_data.get('genre', 'N/A')}")
        logger.info(f"[Formatter] Confidence: {confidence:.2f}")
        return BookData(
            full_title=llm_data.get("full_title", ""),
            short_description=llm_data.get("short_description", ""),
            cover_image_url=cover_url,
            author=llm_data.get("author", ""),
            isbn_13=llm_data.get("isbn_13"),
            isbn_10=llm_data.get("isbn_10"),
            confidence=confidence,
            error=None,
            page_count=self.parse_int(llm_data.get("page_count")),
            publication_year=self.parse_int(llm_data.get("publication_year")),
            genre=llm_data.get("genre") or None,
            language=llm_data.get("language") or None,
            publisher=llm_data.get("publisher") or None
        )

    def format_error(self, error_message: str) -> BookData:
        logger.error(f"[Formatter] Error: {error_message}")
        return BookData(
            full_title="",
            short_description="",
            cover_image_url=None,
            author="",
            isbn_13=None,
            isbn_10=None,
            confidence=0.0,
            error=error_message
        )

    def merge_isbns(self, llm_data: dict, query_isbn: Optional[str]) -> tuple[Optional[str], Optional[str]]:
        isbn_13 = llm_data.get("isbn_13")
        isbn_10 = llm_data.get("isbn_10")

        if not isbn_13 and not isbn_10 and query_isbn:
            if len(query_isbn) == 13:
                isbn_13 = query_isbn
            else:
                isbn_10 = query_isbn

        return isbn_13, isbn_10
