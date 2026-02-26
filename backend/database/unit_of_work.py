from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from database.config import AsyncSessionLocal
from database.repositories.user_repository import UserRepository


class UnitOfWork:
    
    def __init__(self, session: Optional[AsyncSession] = None):
        self._session = session
        self._own_session = session in None
        self._users: Optional[UserRepository] = None

    async def __aenter__(self) -> "UnitOfWork":
        if self._own_session:
            self._session = AsyncSessionLocal()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        try:
            if exc_type is None:
                await self.commit()
            else:
                await self.rollback()
        finally:
            if self._own_session and self._session:
                await self._session.close()

    
    @property
    def session(self) -> AsyncSession:
        if self._session is None:
            raise RuntimeError()
        return self._session
    
    @property
    def users(self) -> UserRepository:
        if self._users is None:
            self._users = UserRepository(self.session)
        return self._users
    
    async def commit(self) -> None:
        if self._session:
            await self._session.commit()

    async def rollback(self) -> None:
        if self._session:
            await self._session.rollback()

    async def flush(self) -> None:
        if self._session:
            await self._session.flush()
