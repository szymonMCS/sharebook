from typing import TypeVar, List, Optional, Type
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from database.interfaces import IRepository, IUserRepository
from src.core.exceptions import DuplicateEntryError, DatabaseError

ModelType = TypeVar("ModelType")

class BaseRepository(IRepository[ModelType]):
    def __init__(self, model: Type[ModelType], db: AsyncSession):
        super().__init__(db)
        self._model = model
    
    async def get(self, id: UUID) -> Optional[ModelType]:
        result = await self._db.execute(
            select(self._model).where(self._model.id == id)
        )
        return result.scalar_one_or_none()
    
    async def get_multi(self, skip: int = 0, limit: int = 100) -> List[ModelType]:
        result = await self._db.execute(
            select(self._model)
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())
    
    async def create(self, obj_in: dict) -> ModelType:
        try:
            db_obj = self._model(**obj_in)
            self._db.add(db_obj)
            await self._db.commit()
            await self._db.refresh(db_obj)
            return db_obj
        except IntegrityError as e:
            await self._db.rollback()
            raise DuplicateEntryError(f"Entity already exists: {e}")
        except SQLAlchemyError as e:
            await self._db.rollback()
            raise DatabaseError(f"Database error: {e}")
    
    async def update(self, db_obj: ModelType, obj_in: dict) -> ModelType:
        try:
            for field, value in obj_in.items():
                setattr(db_obj, field, value)
            await self._db.commit()
            await self._db.refresh(db_obj)
            return db_obj
        except SQLAlchemyError as e:
            await self._db.rollback()
            raise DatabaseError(f"Database error: {e}")
    
    async def delete(self, id: UUID) -> bool:
        try:
            obj = await self.get(id)
            if not obj:
                return False
            await self._db.delete(obj)
            await self._db.commit()
            return True
        except SQLAlchemyError as e:
            await self._db.rollback()
            raise DatabaseError(f"Database error: {e}")
    
    async def exists(self, id: UUID) -> bool:
        result = await self._db.execute(
            select(func.count())
            .where(self._model.id == id)
        )
        return result.scalar() > 0

__all__ = ["BaseRepository", "IUserRepository"]
