import aiofiles
from pathlib import Path
from datetime import datetime
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from database.models import Book
from src.config import settings


class MarkdownGeneratorService:
    def __init__(self, db_session: AsyncSession):
        self._db = db_session
    
    async def generate_catalog(self) -> str:
        result = await self._db.execute(select(Book).order_by(Book.title))
        books = result.scalars().all()
        
        lines = [
            "# Katalog Biblioteki ShareBook",
            "",
            f"*Wygenerowano: {datetime.now().strftime('%Y-%m-%d %H:%M')}*",
            "",
            "## Spis książek",
            "",
        ]
        
        for book in books:
            lines.extend([
                f"### {book.title}",
                "",
                f"- **Autor:** {book.author or 'Nieznany'}",
                f"- **ISBN:** {book.isbn}",
            ])
            
            available_count = sum(1 for ub in book.user_books if ub.status == "available") if book.user_books else 0
            total_count = len(book.user_books) if book.user_books else 0
            
            if total_count > 0:
                status = f"Dostępna ({available_count}/{total_count} egzemplarzy)" if available_count > 0 else f"Wypożyczona (0/{total_count} egzemplarzy)"
            else:
                status = "Brak w kolekcji"
            
            lines.append(f"- **Dostępność:** {status}")
            
            if book.description:
                lines.extend([
                    "",
                    "**Opis:**",
                    f"{book.description}",
                ])
            
            lines.append("")
        
        return "\n".join(lines)
    
    async def save_to_file(self, content: str, path: str | None = None) -> str:
        file_path = Path(path or settings.KNOWLEDGE_BASE_PATH)
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        async with aiofiles.open(file_path, "w", encoding="utf-8") as f:
            await f.write(content)
        
        return str(file_path)
    
    async def regenerate(self, path: str | None = None) -> str:
        content = await self.generate_catalog()
        file_path = await self.save_to_file(content, path)
        return file_path
