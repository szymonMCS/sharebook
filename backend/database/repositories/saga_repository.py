from typing import Optional, List
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from database.models import SagaInstance


class SagaRepository:
    def __init__(self, db: AsyncSession):
        self._db = db
    
    async def get(self, id: UUID) -> Optional[SagaInstance]:
        result = await self._db.execute(select(SagaInstance).where(SagaInstance.id == id))
        return result.scalar_one_or_none()
    
    async def get_by_payload(self, saga_type: str, payload: dict) -> Optional[SagaInstance]:
        result = await self._db.execute(
            select(SagaInstance)
            .where(
                and_(
                    SagaInstance.type == saga_type,
                    SagaInstance.payload == payload
                )
            )
            .order_by(SagaInstance.created_at.desc())
        )
        return result.scalar_one_or_none()
    
    async def get_or_create(self, saga_type: str, payload: dict, status: str = "running") -> SagaInstance:
        existing = await self.get_by_payload(saga_type, payload)
        if existing:
            return existing
        
        saga = SagaInstance(
            type=saga_type,
            status=status,
            payload=payload,
            current_step=0
        )
        self._db.add(saga)
        await self._db.commit()
        await self._db.refresh(saga)
        return saga
    
    async def save(self, saga: SagaInstance) -> SagaInstance:
        await self._db.commit()
        await self._db.refresh(saga)
        return saga
    
    async def get_running_sagas(self, saga_type: Optional[str] = None) -> List[SagaInstance]:
        query = select(SagaInstance).where(SagaInstance.status == "running")
        if saga_type:
            query = query.where(SagaInstance.type == saga_type)
        result = await self._db.execute(query)
        return list(result.scalars().all())
    
    async def get_failed_sagas(self, saga_type: Optional[str] = None) -> List[SagaInstance]:
        query = select(SagaInstance).where(SagaInstance.status == "failed")
        if saga_type:
            query = query.where(SagaInstance.type == saga_type)
        result = await self._db.execute(query)
        return list(result.scalars().all())
    
    async def delete(self, id: UUID) -> bool:
        saga = await self.get(id)
        if not saga:
            return False
        await self._db.delete(saga)
        await self._db.commit()
        return True
