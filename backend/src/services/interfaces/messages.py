from abc import ABC, abstractmethod
from uuid import UUID
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.schemas.loan import MessageResponse, MessageThreadResponse


class IMessageService(ABC):
    @abstractmethod
    async def send_message(self, loan_request_id: UUID, sender_id: UUID, content: str) -> "MessageResponse":
        pass
    @abstractmethod
    async def get_thread(self, loan_request_id: UUID, user_id: UUID) -> "MessageThreadResponse":
        pass
    @abstractmethod
    async def mark_messages_as_read(self, message_id: UUID, user_id: UUID) -> bool:
        pass
    @abstractmethod
    async def mark_all_as_read(self, loan_request_id: UUID, user_id: UUID) -> int:
        pass
    @abstractmethod
    async def add_system_message(self, loan_request_id: UUID, content: str) -> "MessageResponse":
        pass
    @abstractmethod
    async def can_access_thread(self, loan_request_id: UUID, user_id: UUID) -> bool:
        pass
