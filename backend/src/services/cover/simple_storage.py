import logging
from pathlib import Path
from typing import Optional
from src.config import settings

logger = logging.getLogger(__name__)

class SimpleCoverStorage:
    def __init__(self, covers_dir: Optional[Path] = None, file_extension: str = ".jpg"):
        if covers_dir is None:
            covers_dir = Path(settings.COVERS_PATH)

        self.covers_dir = Path(covers_dir)
        self.file_extension = file_extension
        self.covers_dir.mkdir(parents=True, exist_ok=True)

    def _normalize_isbn(self, isbn: str) -> str:
        return isbn.replace("-", "").replace(" ", "").strip()

    def get_cover_path(self, isbn: str) -> Path:
        clean_isbn = self._normalize_isbn(isbn)
        return self.covers_dir / f"{clean_isbn}{self.file_extension}"

    def exists(self, isbn: str) -> bool:
        return self.get_cover_path(isbn).exists()

    def save(self, isbn: str, data: bytes) -> Path:
        cover_path = self.get_cover_path(isbn)
        cover_path.write_bytes(data)
        logger.debug(f"Saved cover for {isbn} to {cover_path}")
        return cover_path

    def load(self, isbn: str) -> Optional[bytes]:
        cover_path = self.get_cover_path(isbn)
        if cover_path.exists():
            return cover_path.read_bytes()
        return None

    def delete(self, isbn: str) -> bool:
        cover_path = self.get_cover_path(isbn)
        if cover_path.exists():
            cover_path.unlink()
            logger.debug(f"Deleted cover for {isbn}")
            return True
        return False

    def get_url_path(self, isbn: str) -> Optional[str]:
        if self.exists(isbn):
            clean_isbn = self._normalize_isbn(isbn)
            return f"/covers/{clean_isbn}{self.file_extension}"
        return None

    def clear_cache(self) -> int:
        count = 0
        for file_path in self.covers_dir.glob(f"*{self.file_extension}"):
            file_path.unlink()
            count += 1
        logger.info(f"Cleared {count} cached covers")
        return count

    def list_covers(self) -> list[str]:
        return [f.stem for f in self.covers_dir.glob(f"*{self.file_extension}")]
