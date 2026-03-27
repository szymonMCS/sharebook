from functools import lru_cache
from sqlalchemy.ext.asyncio import AsyncSession
from src.services.interfaces.factory import IRepositoryFactory, IServiceFactory
from src.services.interfaces.auth import IAuthService, ITokenService
from src.services.interfaces.loans import ILoanService, ILoanRequestService
from src.services.interfaces.messages import IMessageService
from src.services.interfaces.ai import IVectorService, IAIService, IMarkdownGeneratorService
from src.services.interfaces.cover import ICoverService
from src.services.interfaces.book_discovery import IBookDiscoveryService
from database.repositories.user_repository import UserRepository
from database.repositories.book_repository import BookRepository
from database.repositories.user_book_repository import UserBookRepository
from database.repositories.loan_repository import LoanRepository
from database.repositories.loan_request_repository import LoanRequestRepository
from database.repositories.message_repository import MessageRepository
from src.services.auth import AuthService, CookieService, TokenService
from src.services.books import BookService
from src.services.loans import LoanService, LoanRequestService
from src.services.messages import MessageService
from src.services.admin import AdminDashboardService, UserAdminService, BookAdminService
from src.services.ai import (
    VectorService,
    AIService,
    MarkdownGeneratorService,
)
from src.services.cover import ShareBookCoverService
from src.services.book_discovery import UnifiedBookSearch
from src.services.books import UserBookService
from src.config import settings


class RepositoryFactory(IRepositoryFactory):

    def __init__(self, db: AsyncSession):
        self._db = db
    def create_user_repository(self):
        return UserRepository(self._db)
    def create_book_repository(self):
        return BookRepository(self._db)
    def create_user_book_repository(self):
        return UserBookRepository(self._db)
    def create_loan_repository(self):
        return LoanRepository(self._db)
    def create_loan_request_repository(self):
        return LoanRequestRepository(self._db)
    def create_message_repository(self) -> MessageRepository:
        return MessageRepository(self._db)


class ServiceFactory(IServiceFactory):
    def __init__(self, db: AsyncSession | None = None, repo_factory: IRepositoryFactory | None = None):
        if db is None and repo_factory is None:
            raise ValueError("Either db or repo_factory must be provided")
        self._db = db
        self._repo_factory = repo_factory or RepositoryFactory(db)  
    def create_auth_service(self) -> IAuthService:
        assert self._repo_factory is not None
        return AuthService(repository=self._repo_factory.create_user_repository(), book_repo=self._repo_factory.create_book_repository())
    def create_book_service(self) -> BookService:
        assert self._repo_factory is not None
        return BookService(repository=self._repo_factory.create_book_repository())
    def create_loan_service(self) -> ILoanService:
        assert self._repo_factory is not None
        return LoanService(
            loan_repo=self._repo_factory.create_loan_repository(),
            user_repo=self._repo_factory.create_user_repository(),
            user_book_repo=self._repo_factory.create_user_book_repository()
        )
    def create_loan_request_service(self) -> ILoanRequestService:
        assert self._repo_factory is not None
        assert self._db is not None
        return LoanRequestService(
            request_repo=self._repo_factory.create_loan_request_repository(),
            loan_repo=self._repo_factory.create_loan_repository(),
            user_book_repo=self._repo_factory.create_user_book_repository(),
            message_repo=self._repo_factory.create_message_repository(),
            db=self._db
        )
    def create_message_service(self) -> IMessageService:
        assert self._repo_factory is not None
        return MessageService(
            message_repo=self._repo_factory.create_message_repository(),
            request_repo=self._repo_factory.create_loan_request_repository(),
            user_book_repo=self._repo_factory.create_user_book_repository()
        )
    def create_cover_service(self) -> ICoverService:
        return ShareBookCoverService(openai_api_key=settings.OPENAI_API_KEY)
    def create_admin_dashboard_service(self) -> AdminDashboardService:
        assert self._repo_factory is not None
        return AdminDashboardService(
            user_repo=self._repo_factory.create_user_repository(),
            book_repo=self._repo_factory.create_book_repository(),
            loan_repo=self._repo_factory.create_loan_repository(),
            user_book_repo=self._repo_factory.create_user_book_repository()
        )
    def create_user_admin_service(self) -> UserAdminService:
        assert self._repo_factory is not None
        assert self._db is not None
        return UserAdminService(
            db=self._db,
            user_repo=self._repo_factory.create_user_repository(),
            user_book_repo=self._repo_factory.create_user_book_repository(),
            loan_repo=self._repo_factory.create_loan_repository()
        )
    def create_book_admin_service(self) -> BookAdminService:
        assert self._repo_factory is not None
        assert self._db is not None
        return BookAdminService(
            db=self._db,
            book_repo=self._repo_factory.create_book_repository(),
            user_book_repo=self._repo_factory.create_user_book_repository(),
            loan_repo=self._repo_factory.create_loan_repository()
        )
    def create_book_discovery_service(self) -> IBookDiscoveryService:
        return UnifiedBookSearch(openai_api_key=settings.OPENAI_API_KEY)
    def create_vector_service(self) -> IVectorService:
        assert self._db is not None
        return VectorService(vector_db=self._db)
    def create_ai_service(self) -> IAIService:
        vector_service = self.create_vector_service()
        return AIService(vector_service=vector_service)
    def create_markdown_generator_service(self) -> IMarkdownGeneratorService:
        assert self._db is not None
        return MarkdownGeneratorService(db_session=self._db)
    def create_user_book_service(self) -> UserBookService:
        assert self._db is not None
        assert self._repo_factory is not None
        return UserBookService(
            db=self._db,
            user_book_repo=self._repo_factory.create_user_book_repository(),
            book_repo=self._repo_factory.create_book_repository(),
            user_repo=self._repo_factory.create_user_repository()
        )
    def create_token_service(self) -> TokenService:
        return TokenService()
    def create_user_service(self) -> IAuthService:
        return self.create_auth_service()
    def create_registration_service(self) -> IAuthService:
        return self.create_auth_service()
    def create_password_service(self) -> IAuthService:
        return self.create_auth_service()
    def create_book_catalog_service(self) -> BookService:
        return self.create_book_service()
    def create_library_management_service(self) -> UserBookService:
        return self.create_user_book_service()
