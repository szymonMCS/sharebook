from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from enum import Enum
from uuid import UUID


class EnrichmentField(Enum):
    TITLE = "title"
    AUTHOR = "author"
    DESCRIPTION = "description"
    PUBLISHER = "publisher"
    PUBLICATION_YEAR = "publication_year"
    PAGE_COUNT = "page_count"
    GENRE = "genre"
    COVER_URL = "cover_url"
    LANGUAGE = "language"


@dataclass
class EnrichmentData:
    source: str
    fields: Dict[EnrichmentField, Any] = field(default_factory=dict)
    confidence: float = 0.0
    raw_data: Optional[Dict] = None

    def has_field(self, field: EnrichmentField) -> bool:
        return field in self.fields and self.fields[field] is not None


@dataclass
class EnrichmentContext:
    book_id: UUID
    isbn: Optional[str]
    current_title: str
    current_author: Optional[str]
    current_description: Optional[str]
    current_genre: Optional[str]
    current_publisher: Optional[str]
    current_publication_year: Optional[int]
    current_page_count: Optional[int]


@dataclass
class EnrichmentResult:
    book_id: UUID
    status: str
    changes: List[str] = field(default_factory=list)
    sources_used: List[str] = field(default_factory=list)
    error: Optional[str] = None


class IEnrichmentAdapter(ABC):
    @property
    @abstractmethod
    def source_name(self) -> str:
        pass
    @property
    @abstractmethod
    def supported_fields(self) -> List[EnrichmentField]:
        pass
    @abstractmethod
    async def enrich(self, context: EnrichmentContext) -> EnrichmentData:
        pass
    @abstractmethod
    def is_available(self) -> bool:
        pass
    def can_enrich_field(self, field: EnrichmentField) -> bool:
        return field in self.supported_fields


class IEnrichmentStrategy(ABC):
    @abstractmethod
    def get_adapter_order(self, adapters: List[IEnrichmentAdapter], context: EnrichmentContext) -> List[IEnrichmentAdapter]:
        pass
    @abstractmethod
    def should_enrich_field(self, field: EnrichmentField, current_value: Any, proposed_value: Any, adapter_confidence: float) -> bool:
        pass
    @abstractmethod
    def merge_data(self, context: EnrichmentContext, adapter_results: List[EnrichmentData]) -> Dict[EnrichmentField, Any]:
        pass


class IEnrichmentOrchestrator(ABC):
    @abstractmethod
    async def enrich_book(self, book_id: UUID) -> EnrichmentResult:
        pass
    @abstractmethod
    async def enrich_multiple(self, book_ids: List[UUID]) -> List[EnrichmentResult]:
        pass
