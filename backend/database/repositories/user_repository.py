from typing import Optional, List
from uuid import UUID
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_
from database.models import User, Loan
from database.interfaces import IUserRepository
from .base import BaseRepository


class UserRepository(BaseRepository[User], IUserRepository):
    def __init__(self, db: AsyncSession):
        super().__init__(User, db)
    
    async def get_by_id(self, id: UUID) -> Optional[User]:
        return await self.get(id)
    
    async def get_by_id_for_update(self, id: UUID) -> Optional[User]:
        result = await self._db.execute(select(User).where(User.id == id).with_for_update())
        return result.scalar_one_or_none()
    
    async def get_by_email(self, email: str) -> Optional[User]:
        result = await self._db.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()
    
    async def email_exists(self, email: str) -> bool:
        result = await self._db.execute(select(func.count()).where(User.email == email))
        return result.scalar() > 0
    
    async def get_multi(self, skip: int = 0, limit: int = 100) -> tuple[List[User], int]:
        count_result = await self._db.execute(select(func.count()).select_from(User))
        total = count_result.scalar() or 0  
        result = await self._db.execute(select(User).offset(skip).limit(limit))
        users = list(result.scalars().all())
        
        return users, total

    async def count_user_books(self, user_id: UUID) -> int:
        from sqlalchemy import func
        from database.models import UserBook
        result = await self._db.execute(select(func.count()).where(UserBook.user_id == user_id))
        return result.scalar() or 0

    async def get_multi_with_filters(
        self, 
        skip: int = 0, 
        limit: int = 100,
        search: Optional[str] = None,
        role: Optional[str] = None,
        is_active: Optional[bool] = None
    ) -> tuple[List[User], int]:
        query = select(User)
        count_query = select(func.count()).select_from(User)
        
        if search:
            search_filter = or_(
                User.email.ilike(f"%{search}%"),
                User.first_name.ilike(f"%{search}%"),
                User.last_name.ilike(f"%{search}%")
            )
            query = query.where(search_filter)
            count_query = count_query.where(search_filter)
        
        if role:
            query = query.where(User.role == role)
            count_query = count_query.where(User.role == role)
        
        if is_active is not None:
            query = query.where(User.is_active == is_active)
            count_query = count_query.where(User.is_active == is_active)
        
        count_result = await self._db.execute(count_query)
        total = count_result.scalar() or 0
        
        query = query.offset(skip).limit(limit)
        result = await self._db.execute(query)
        users = list(result.scalars().all())
        
        return users, total

    async def count_all(self) -> int:
        result = await self._db.execute(select(func.count()).select_from(User))
        return result.scalar() or 0

    async def count_new_since(self, since: datetime) -> int:
        result = await self._db.execute(select(func.count()).select_from(User).where(User.created_at >= since))
        return result.scalar() or 0

    async def count_active_borrowers(self, since: datetime) -> int:
        result = await self._db.execute(select(func.count(func.distinct(Loan.borrower_id))).where(Loan.created_at >= since))
        return result.scalar() or 0

    async def get_daily_registrations(self, days: int) -> List[dict]:
        from datetime import timezone, timedelta
        since = datetime.now(timezone.utc) - timedelta(days=days)
        
        stmt = (
            select(func.date(User.created_at).label("date"), func.count().label("count"))
            .where(User.created_at >= since)
            .group_by(func.date(User.created_at))
            .order_by(func.date(User.created_at))
        )
        result = await self._db.execute(stmt)
        return [{"date": str(row.date), "count": row.count} for row in result.all()]
