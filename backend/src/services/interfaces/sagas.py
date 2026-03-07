from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional, Any, Dict
from uuid import UUID


@dataclass
class SagaResult:
    success: bool
    data: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None


@dataclass
class SagaContext:
    saga_id: UUID
    current_step: int
    payload: Dict[str, Any]
    status: str = "running"


class ISagaStep(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        pass
    @abstractmethod
    async def execute(self, context: SagaContext) -> bool:
        pass
    @abstractmethod
    async def compensate(self, context: SagaContext) -> bool:
        pass


class ISaga(ABC):
    @abstractmethod
    async def execute(self, **kwargs) -> SagaResult:
        pass
