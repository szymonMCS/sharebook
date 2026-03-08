import logging
from uuid import UUID
from typing import Optional
from database.interfaces import IMessageRepository

logger = logging.getLogger(__name__)


class LoanRequestMessageHandler:
    def __init__(self, message_repo: Optional[IMessageRepository] = None):
        self._message_repo = message_repo
    
    async def add_system_message(self, loan_request_id: UUID, content: str) -> None:
        if self._message_repo:
            await self._message_repo.create_system_message(loan_request_id=loan_request_id, content=content)
            logger.debug(f"System message added to request {loan_request_id}")
    
    async def notify_reserved(self, request_id: UUID) -> None:
        await self.add_system_message(loan_request_id=request_id, content="Właściciel zarezerwował książkę dla Ciebie. Książka oczekuje na odbiór.")
    
    async def notify_accepted(self, request_id: UUID, due_date: str) -> None:
        await self.add_system_message(loan_request_id=request_id, content=f"Właściciel zaakceptował wypożyczenie. Książka została wypożyczona do {due_date}.")
    
    async def notify_rejected(self, request_id: UUID, reason: Optional[str] = None) -> None:
        if reason:
            content = f"Właściciel odrzucił prośbę: {reason}"
        else:
            content = "Właściciel odrzucił prośbę o wypożyczenie."
        await self.add_system_message(request_id, content)
    
    async def notify_auto_rejected(self, request_id: UUID, reason: str) -> None:
        await self.add_system_message(loan_request_id=request_id, content=f"Właściciel odrzucił prośbę: {reason}")
    
    async def notify_request_created(self, request_id: UUID) -> None:
        await self.add_system_message(loan_request_id=request_id, content="Prośba o wypożyczenie została utworzona.")
    
    async def notify_cancelled(self, request_id: UUID) -> None:
        await self.add_system_message(loan_request_id=request_id, content="Prośba o wypożyczenie została anulowana przez proszącego.")
