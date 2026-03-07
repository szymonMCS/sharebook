import logging
import re
from functools import lru_cache
from pathlib import Path
from typing import Optional
from src.config import settings

logger = logging.getLogger(__name__)


class CoverStorage:
    ISBN_PATTERN = re.compile(r'^[0-9]{9}[0-9Xx]$|^[0-9]{13}$')

    def __init__(self, covers_dir: Optional[Path] = None, file_extension: str = ".jpg"):
        if covers_dir is None:
            covers_dir = Path(settings.COVERS_PATH)

        self.covers_dir = Path(covers_dir)
        self.file_extension = file_extension
        self.covers_dir.mkdir(parents=True, exist_ok=True)

    def _normalize_isbn(self, isbn: str) -> str:
        return isbn.replace("-", "").replace(" ", "").strip()

    def _validate_isbn(self, isbn: str) -> str:
        clean = isbn.replace("-", "").replace(" ", "").strip().upper()
        if not self.ISBN_PATTERN.match(clean):
            raise ValueError(f"Invalid ISBN format: {isbn}")
        return clean

    def get_cover_path(self, isbn: str) -> Path:
        clean_isbn = self._validate_isbn(isbn)
        path = self.covers_dir / f"{clean_isbn}{self.file_extension}"
        try:
            path.resolve().relative_to(self.covers_dir.resolve())
        except ValueError:
            raise ValueError(f"Path traversal detected: {isbn}")
        return path

    @lru_cache(maxsize=1024)
    def exists(self, isbn: str) -> bool:
        return self.get_cover_path(isbn).exists()

    def save(self, isbn: str, data: bytes) -> Path:
        try:
            cover_path = self.get_cover_path(isbn)
            cover_path.write_bytes(data)
            logger.info(f"[CoverStorage] Saved cover for {isbn} to {cover_path}")
            return cover_path
        except IOError as e:
            logger.error(f"[CoverStorage] Failed to save cover for {isbn}: {e}")
            raise

    def load(self, isbn: str) -> Optional[bytes]:
        try:
            cover_path = self.get_cover_path(isbn)
            if cover_path.exists():
                return cover_path.read_bytes()
            return None
        except IOError as e:
            logger.error(f"[CoverStorage] Failed to load cover for {isbn}: {e}")
            return None

    def delete(self, isbn: str) -> bool:
        try:
            cover_path = self.get_cover_path(isbn)
            if cover_path.exists():
                cover_path.unlink()
                logger.info(f"[CoverStorage] Deleted cover for {isbn}")
                return True
            return False
        except IOError as e:
            logger.error(f"[CoverStorage] Failed to delete cover for {isbn}: {e}")
            return False

    def get_url_path(self, isbn: str) -> Optional[str]:
        if self.exists(isbn):
            clean_isbn = self._normalize_isbn(isbn)
            return f"/covers/{clean_isbn}{self.file_extension}"
        return None

    def clear_cache(self) -> int:
        count = 0
        for file_path in self.covers_dir.glob(f"*{self.file_extension}"):
            try:
                file_path.unlink()
                count += 1
            except IOError as e:
                logger.warning(f"[CoverStorage] Failed to delete {file_path}: {e}")
        logger.info(f"[CoverStorage] Cleared {count} cached covers")
        return count

    def list_covers(self) -> list[str]:
        return [f.stem for f in self.covers_dir.glob(f"*{self.file_extension}")]
