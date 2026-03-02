from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from database.config import AsyncSessionLocal
from database.repositories.user_repository import UserRepository
from database.repositories.book_repository import BookRepository
from database.repositories.user_book_repository import UserBookRepository


class UnitOfWork:
    """Pattern Unit of Work do zarządzania wyporzyczeniami i repozytoriami"""

    def __init__(self, session: Optional[AsyncSession] = None):
        self._session = session
        self._own_session = session is None
        self._users: Optional[UserRepository] = None
        self._books: Optional[BookRepository] = None
        self._user_books: Optional[UserBookRepository] = None

    async def __aenter__(self) -> "UnitOfWork":
        if self._own_session:
            self._session = AsyncSessionLocal()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> bool:
        """
        Obsługa wyjścia z context manager.
        Zwraca True jeśli wyjątek został obsłużony, False w przeciwnym razie.
        """
        try:
            if exc_type is None:
                await self.commit()
            else:
                await self.rollback()
        except Exception:
            await self.rollback()
            raise
        finally:
            if self._own_session and self._session:
                await self._session.close()
        return False  # Nie tłumimy wyjątków

    @property
    def session(self) -> AsyncSession:
        if self._session is None:
            raise RuntimeError("Session not initialized")
        return self._session

    @property
    def users(self) -> UserRepository:
        if self._users is None:
            self._users = UserRepository(self.session)
        return self._users

    @property
    def books(self) -> BookRepository:
        if self._books is None:
            self._books = BookRepository(self.session)
        return self._books

    @property
    def user_books(self) -> UserBookRepository:
        if self._user_books is None:
            self._user_books = UserBookRepository(self.session)
        return self._user_books

    async def commit(self) -> None:
        if self._session:
            await self._session.commit()

    async def rollback(self) -> None:
        if self._session:
            await self._session.rollback()

    async def flush(self) -> None:
        if self._session:
            await self._session.flush()
