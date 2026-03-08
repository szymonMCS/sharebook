import re
from dataclasses import dataclass
from typing import Optional


@dataclass
class SearchQuery:
    original: str
    cleaned: str
    is_isbn: bool
    normalized_isbn: Optional[str] = None


class QueryBuilder:
    @staticmethod
    def normalize_isbn(isbn: str) -> str:
        return re.sub(r'[\s\-]', '', isbn)

    @staticmethod
    def is_isbn(query: str) -> bool:
        cleaned = QueryBuilder.normalize_isbn(query)
        return cleaned.isdigit() and len(cleaned) in [10, 13]

    def build(self, query: str) -> Optional[SearchQuery]:
        if not query or not query.strip():
            return None

        cleaned = query.strip()
        is_isbn = self.is_isbn(cleaned)
        normalized_isbn = self.normalize_isbn(cleaned) if is_isbn else None

        return SearchQuery(
            original=query,
            cleaned=cleaned,
            is_isbn=is_isbn,
            normalized_isbn=normalized_isbn
        )

    def build_prompt(self, query: SearchQuery) -> str:
        return f"Znajdź książkę: {query.cleaned}"

    @staticmethod
    def get_system_prompt() -> str:
        return """Jesteś ekspertem bibliotecznym. Znajdź DOKŁADNE informacje o książce.

Zasady:
1. UŻYJ web search - model ma dostęp do internetu
2. TYTUŁ: Pełny tytuł w języku polskim lub oryginalnym
3. OPIS: Szczegółowy opis około 800-1000 znaków. Zacznij od gatunku, potem przedstaw fabułę, bohaterów i tematykę bez spoilerów.
4. AUTOR: Imię i nazwisko
5. ISBN-13: 13 cyfr bez myślników (jeśli dostępne)
6. ISBN-10: 10 cyfr bez myślników (jeśli dostępne)
7. PAGE_COUNT: Liczba stron (tylko liczba, np. 432)
8. PUBLICATION_YEAR: Rok pierwszego wydania (tylko rok, np. 2019)
9. GENRE: Główny gatunek literacki (np. "Thriller psychologiczny", "Literatura piękna", "Fantasy")
10. LANGUAGE: Język oryginału (np. "polski", "angielski")
11. PUBLISHER: Wydawca książki

Zwróć STRICT JSON bez komentarzy:
{
  "full_title": "string",
  "short_description": "string (800-1000 znaków)",
  "author": "string",
  "isbn_13": "string lub null",
  "isbn_10": "string lub null",
  "page_count": liczba lub null,
  "publication_year": liczba lub null,
  "genre": "string lub null",
  "language": "string lub null",
  "publisher": "string lub null",
  "confidence": 0.0-1.0,
  "error": "string lub null"
}"""
