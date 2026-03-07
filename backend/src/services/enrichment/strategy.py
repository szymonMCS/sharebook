from typing import Any, Dict, List
from src.services.enrichment.interfaces import IEnrichmentStrategy, IEnrichmentAdapter, EnrichmentContext, EnrichmentData, EnrichmentField
from src.core.constants import PLACEHOLDER_TITLE


class DefaultEnrichmentStrategy(IEnrichmentStrategy):
    PRIORITY = {
        "google_books": 1,
        "openai": 2,
    }

    def get_adapter_order(self, adapters: List[IEnrichmentAdapter], context: EnrichmentContext) -> List[IEnrichmentAdapter]:
        return sorted(adapters, key=lambda a: self.PRIORITY.get(a.source_name, 99))

    def should_enrich_field(self, field: EnrichmentField, current_value: Any, proposed_value: Any, adapter_confidence: float) -> bool:
        if not proposed_value:
            return False

        if not current_value:
            return True

        if field == EnrichmentField.DESCRIPTION:
            return len(str(proposed_value)) > len(str(current_value)) * 1.2

        if field == EnrichmentField.TITLE and current_value in [PLACEHOLDER_TITLE, "", None]:
            return True

        return False

    def merge_data(self, context: EnrichmentContext, adapter_results: List[EnrichmentData]) -> Dict[EnrichmentField, Any]:
        merged = {}
        for result in adapter_results:
            for field, value in result.fields.items():
                if field not in merged:
                    merged[field] = value
        return merged
