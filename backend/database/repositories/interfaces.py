from abc import ABC, abstractmethod
from typing import Optional, List, TypeVar, Generic
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession

ModelType = TypeVar("ModelType")

class IRepository(ABC, Generic[ModelType]):

    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    @abstractmethod
    async def get(self, id: UUID) -> Optional[ModelType]:
        pass

    @abstractmethod
    async def create(self, obj_in: dict) -> ModelType:
        pass

    @abstractmethod
    async def update(self, db_obj: ModelType, obj_in: dict) -> ModelType:
        pass


class IUserRepository(IRepository["User"], ABC):

    @abstractmethod
    async def get_by_email(self, email: str) -> Optional["User"]:
        pass

    @abstractmethod
    async def email_exists(self, email: str) -> bool:
        pass

