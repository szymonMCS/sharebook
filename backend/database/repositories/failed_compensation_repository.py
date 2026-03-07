from typing import Optional, List
from uuid import UUID
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from database.models import FailedCompensation


class FailedCompensationRepository:
    def __init__(self, db: AsyncSession):
        self._db = db
    
    async def create(
        self,
        compensation_type: str,
        error_message: str,
        saga_instance_id: Optional[UUID] = None,
        entity_id: Optional[UUID] = None,
        error_details: Optional[dict] = None
    ) -> FailedCompensation:
        failed = FailedCompensation(
            saga_instance_id=saga_instance_id,
            compensation_type=compensation_type,
            entity_id=entity_id,
            error_message=error_message,
            error_details=error_details,
            status="pending"
        )
        self._db.add(failed)
        await self._db.commit()
        await self._db.refresh(failed)
        return failed
    
    async def get(self, id: UUID) -> Optional[FailedCompensation]:
        result = await self._db.execute(select(FailedCompensation).where(FailedCompensation.id == id))
        return result.scalar_one_or_none()
    
    async def get_pending(self) -> List[FailedCompensation]:
        result = await self._db.execute(
            select(FailedCompensation)
            .where(FailedCompensation.status == "pending")
            .order_by(FailedCompensation.created_at.desc())
        )
        return list(result.scalars().all())
    
    async def get_by_saga(self, saga_instance_id: UUID) -> List[FailedCompensation]:
        result = await self._db.execute(
            select(FailedCompensation)
            .where(FailedCompensation.saga_instance_id == saga_instance_id)
            .order_by(FailedCompensation.created_at.desc())
        )
        return list(result.scalars().all())
    
    async def resolve(self, id: UUID, resolved_by: Optional[UUID] = None, notes: Optional[str] = None) -> Optional[FailedCompensation]:
        failed = await self.get(id)
        if not failed:
            return None
        
        failed.status = "resolved"
        failed.resolved_at = datetime.now(timezone.utc)
        failed.resolved_by = resolved_by
        if notes:
            failed.notes = notes
        
        await self._db.commit()
        await self._db.refresh(failed)
        return failed
    
    async def mark_permanent_failure(self, id: UUID, notes: Optional[str] = None) -> Optional[FailedCompensation]:
        failed = await self.get(id)
        if not failed:
            return None
        
        failed.status = "failed_permanent"
        if notes:
            failed.notes = notes
        
        await self._db.commit()
        await self._db.refresh(failed)
        return failed
