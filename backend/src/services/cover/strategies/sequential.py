from src.services.interfaces import ISourceStrategy, ICoverSource, CoverResult, CoverSourceType


class SequentialSourceStrategy(ISourceStrategy):
    async def fetch_cover(
        self,
        sources: list[ICoverSource],
        isbn: str,
        book_title: str | None = None,
        book_author: str | None = None,
        book_genre: str | None = None
    ) -> CoverResult:
        sorted_sources = sorted(sources, key=lambda s: s.get_priority())

        for source in sorted_sources:
            if not source.is_available():
                continue

            result = await source.fetch_cover(isbn, book_title, book_author, book_genre)
            if result.success:
                return result

        return CoverResult(
            isbn=isbn.replace("-", "").replace(" ", "").strip(),
            success=False,
            error="All sources failed",
            source=CoverSourceType.NONE
        )
