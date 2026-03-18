import logging
from uuid import UUID
from typing import Optional

logger = logging.getLogger(__name__)


class LoanRequestMessageHandler:
    def __init__(self, message_repo: Optional[any] = None):
        pass
    async def add_system_message(self, loan_request_id: UUID, content: str) -> None:
        pass
    async def notify_reserved(self, request_id: UUID) -> None:
        pass
    async def notify_accepted(self, request_id: UUID, due_date: str) -> None:
        pass
    async def notify_rejected(self, request_id: UUID, reason: Optional[str] = None) -> None:
        pass
    async def notify_auto_rejected(self, request_id: UUID, reason: str) -> None:
        pass
    async def notify_request_created(self, request_id: UUID) -> None:
        pass
    async def notify_cancelled(self, request_id: UUID) -> None:
        pass
