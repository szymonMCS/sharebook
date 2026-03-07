from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List, Any
from uuid import UUID


@dataclass
class DashboardStats:
    total_users: int
    total_books: int
    total_loans: int
    pending_requests: int
    active_loans: int
    new_users_today: int
    new_books_today: int
    generated_at: datetime


@dataclass
class UserListResult:
    data: List[dict]
    total: int
    page: int
    per_page: int
    total_pages: int


@dataclass
class BookListResult:
    data: List[dict]
    total: int
    page: int
    per_page: int
    total_pages: int


class IAdminDashboardService(ABC):
    @abstractmethod
    async def get_dashboard_stats(self) -> DashboardStats:
        pass
    @abstractmethod
    async def get_user_stats(self, days: int = 30) -> dict:
        pass
    @abstractmethod
    async def get_book_stats(self, days: int = 30) -> dict:
        pass
    @abstractmethod
    async def get_loan_stats(self, days: int = 30) -> dict:
        pass


class IUserAdminService(ABC):
    @abstractmethod
    async def list_users(
        self,
        page: int = 1,
        per_page: int = 20,
        search: Optional[str] = None,
        role: Optional[str] = None,
        is_active: Optional[bool] = None
    ) -> UserListResult:
        pass
    @abstractmethod
    async def get_user_details(self, user_id: UUID) -> dict:
        pass
    @abstractmethod
    async def update_user_role(self, user_id: UUID, new_role: str, current_admin_id: UUID) -> dict:
        pass
    @abstractmethod
    async def reset_user_password(self, user_id: UUID, current_admin_id: UUID) -> dict:
        pass
    @abstractmethod
    async def deactivate_user(self, user_id: UUID, current_admin_id: UUID) -> dict:
        pass
    @abstractmethod
    async def activate_user(self, user_id: UUID, current_admin_id: UUID) -> dict:
        pass
    @abstractmethod
    async def delete_user(self, user_id: UUID, current_admin_id: UUID, hard_delete: bool = False) -> None:
        pass


class IBookAdminService(ABC):
    @abstractmethod
    async def list_books(
        self,
        page: int = 1,
        per_page: int = 20,
        search: Optional[str] = None,
        has_loans: Optional[bool] = None
    ) -> BookListResult:
        pass
    
    @abstractmethod
    async def get_book_details(self, book_id: UUID) -> dict:
        pass
    @abstractmethod
    async def delete_book(self, book_id: UUID, force: bool = False) -> dict:
        pass
    @abstractmethod
    async def merge_books(self, source_book_id: UUID, target_book_id: UUID) -> dict:
        pass
    @abstractmethod
    async def update_book_metadata(self, book_id: UUID, metadata: dict) -> dict:
        pass
