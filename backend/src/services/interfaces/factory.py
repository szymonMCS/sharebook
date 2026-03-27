from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.services.admin.interfaces import IAdminDashboardService, IUserAdminService, IBookAdminService


IUserRepository = "IUserRepository"
IBookRepository = "IBookRepository"
IUserBookRepository = "IUserBookRepository"
ILoanRepository = "ILoanRepository"
ILoanRequestRepository = "ILoanRequestRepository"


class IRepositoryFactory(ABC):
    @abstractmethod
    def create_user_repository(self) -> IUserRepository:
        pass
    @abstractmethod
    def create_book_repository(self) -> IBookRepository:
        pass
    @abstractmethod
    def create_user_book_repository(self) -> IUserBookRepository:
        pass
    @abstractmethod
    def create_loan_repository(self) -> ILoanRepository:
        pass
    @abstractmethod
    def create_loan_request_repository(self) -> ILoanRequestRepository:
        pass


class IServiceFactory(ABC):
    @abstractmethod
    def create_auth_service(self):
        pass
    @abstractmethod
    def create_user_service(self):
        pass
    @abstractmethod
    def create_registration_service(self):
        pass
    @abstractmethod
    def create_token_service(self):
        pass
    @abstractmethod
    def create_password_service(self):
        pass
    @abstractmethod
    def create_book_catalog_service(self):
        pass
    @abstractmethod
    def create_library_management_service(self):
        pass
    @abstractmethod
    def create_loan_service(self):
        pass
    @abstractmethod
    def create_loan_request_service(self):
        pass
    @abstractmethod
    def create_message_service(self):
        pass
    @abstractmethod
    def create_admin_dashboard_service(self) -> "IAdminDashboardService":
        pass
    @abstractmethod
    def create_user_admin_service(self) -> "IUserAdminService":
        pass
    @abstractmethod
    def create_book_admin_service(self) -> "IBookAdminService":
        pass
    # Book Discovery and AI services
    @abstractmethod
    def create_book_discovery_service(self):
        """Create book discovery service for AI-powered book search."""
        pass
    @abstractmethod
    def create_vector_service(self):
        """Create vector service for embeddings and similarity search."""
        pass
    @abstractmethod
    def create_ai_service(self):
        """Create AI service for RAG-based recommendations."""
        pass
    @abstractmethod
    def create_markdown_generator_service(self):
        """Create markdown generator service for knowledge base."""
        pass
    @abstractmethod
    def create_cover_service(self):
        """Create cover service for fetching book covers."""
        pass
    @abstractmethod
    def create_user_book_service(self):
        """Create user book service for library management."""
        pass
