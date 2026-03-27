from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.services.interfaces.auth import IAuthService, ITokenService
    from src.services.interfaces.loans import ILoanService, ILoanRequestService
    from src.services.interfaces.messages import IMessageService
    from src.services.interfaces.ai import IVectorService, IAIService, IMarkdownGeneratorService
    from src.services.interfaces.cover import ICoverService
    from src.services.interfaces.book_discovery import IBookDiscoveryService
    from src.services.books import BookService, UserBookService


class IRepositoryFactory(ABC):
    @abstractmethod
    def create_user_repository(self):
        pass
    @abstractmethod
    def create_book_repository(self):
        pass
    @abstractmethod
    def create_user_book_repository(self):
        pass
    @abstractmethod
    def create_loan_repository(self):
        pass
    @abstractmethod
    def create_loan_request_repository(self):
        pass
    @abstractmethod
    def create_message_repository(self):
        pass


class IServiceFactory(ABC):
    @abstractmethod
    def create_auth_service(self) -> "IAuthService":
        pass
    @abstractmethod
    def create_user_service(self) -> "IAuthService":
        pass
    @abstractmethod
    def create_registration_service(self) -> "IAuthService":
        pass
    @abstractmethod
    def create_token_service(self) -> "ITokenService":
        pass
    @abstractmethod
    def create_password_service(self) -> "IAuthService":
        pass
    @abstractmethod
    def create_book_catalog_service(self) -> "BookService":
        pass
    @abstractmethod
    def create_library_management_service(self) -> "UserBookService":
        pass
    @abstractmethod
    def create_loan_service(self) -> "ILoanService":
        pass
    @abstractmethod
    def create_loan_request_service(self) -> "ILoanRequestService":
        pass
    @abstractmethod
    def create_message_service(self) -> "IMessageService":
        pass
    @abstractmethod
    def create_admin_dashboard_service(self):
        pass
    @abstractmethod
    def create_user_admin_service(self):
        pass
    @abstractmethod
    def create_book_admin_service(self):
        pass
    @abstractmethod
    def create_book_discovery_service(self) -> "IBookDiscoveryService":
        pass
    @abstractmethod
    def create_vector_service(self) -> "IVectorService":
        pass
    @abstractmethod
    def create_ai_service(self) -> "IAIService":
        pass
    @abstractmethod
    def create_markdown_generator_service(self) -> "IMarkdownGeneratorService":
        pass
    @abstractmethod
    def create_cover_service(self) -> "ICoverService":
        pass
    @abstractmethod
    def create_user_book_service(self) -> "UserBookService":
        pass
