from pydantic import BaseModel, Field


class Chunk(BaseModel):
    headline: str = Field(
        description="Nagłówek prawdopodobnie użyty w zapytaniu użytkownika"
    )
    summary: str = Field(
        description="Podsumowanie zawartości fragmentu (2-3 zdania)"
    )
    original_text: str = Field(
        description="Dokładny, oryginalny tekst fragmentu do wyszukiwania"
    )


class Chunks(BaseModel):
    chunks: list[Chunk]
    
    def to_texts(self) -> list[str]:
        """Konwertuj chunki na teksty do embeddingu.
        
        Łączy headline + summary + original_text dla bogatszego kontekstu.
        """
        return [
            f"{chunk.headline}\n\n{chunk.summary}\n\n{chunk.original_text}"
            for chunk in self.chunks
        ]
