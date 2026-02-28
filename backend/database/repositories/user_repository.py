from typing import Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from database.models import User
from database.interfaces import IUserRepository
from .base import BaseRepository


class UserRepository(BaseRepository[User], IUserRepository):
    def __init__(self, db: AsyncSession):
        super().__init__(User, db)
    
    async def get_by_id(self, id: UUID) -> Optional[User]:
        return await self.get(id)
    
    async def get_by_email(self, email: str) -> Optional[User]:
        result = await self._db.execute(
            select(User).where(User.email == email)
        )
        return result.scalar_one_or_none()
    
    async def email_exists(self, email: str) -> bool:
        result = await self._db.execute(
            select(User).where(User.email == email)
        )
        return result.scalar_one_or_none() is not None
