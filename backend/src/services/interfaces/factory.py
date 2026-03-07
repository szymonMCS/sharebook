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
    def create_book_import_service(self):
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
    @abstractmethod
    def create_embedding_service(self):
        pass
    @abstractmethod
    def create_vector_search_service(self):
        pass
    @abstractmethod
    def create_book_indexing_service(self):
        pass
    @abstractmethod
    def create_cover_manager(self):
        pass
    @abstractmethod
    def create_enrichment_orchestrator(self):
        pass
    @abstractmethod
    def create_loan_acceptance_saga(self):
        pass
