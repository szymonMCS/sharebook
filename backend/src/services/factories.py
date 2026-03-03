from sqlalchemy.ext.asyncio import AsyncSession
from src.services.interfaces import (
    IRepositoryFactory,
    IServiceFactory,
    IAuthService,
    IUserService,
    IRegistrationService,
    ITokenService,
    IPasswordService,
    IBookCatalogService,
    ILibraryManagementService,
    ICommunityBookService,
    IBookImportService,
    IBookMetadataProvider,
    ILoanService,
    ILoanRequestService,
    IMessageService,
)
from database.repositories.user_repository import UserRepository
from database.repositories.book_repository import BookRepository
from database.repositories.user_book_repository import UserBookRepository
from database.repositories.loan_repository import LoanRepository
from database.repositories.loan_request_repository import LoanRequestRepository
from database.repositories.message_repository import MessageRepository
from src.services.auth_service import AuthService
from src.services.user_service import UserService
from src.services.registration_service import RegistrationService
from src.services.token_service import TokenService
from src.services.password_service import PasswordService
from src.services.book_catalog_service import BookCatalogService
from src.services.library_management_service import LibraryManagementService
from src.services.community_book_service import CommunityBookService
from src.services.book_import_service import BookImportService
from src.services.loan_service import LoanService
from src.services.loan_request_service import LoanRequestService
from src.services.message_service import MessageService
from src.services.google_books_provider import GoogleBooksProvider


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

    def create_message_repository(self):
        return MessageRepository(self._db)


class ServiceFactory(IServiceFactory):

    def __init__(
        self, 
        db: AsyncSession = None, 
        repo_factory: IRepositoryFactory = None,
        metadata_provider: IBookMetadataProvider = None
    ):
        self._db = db
        self._repo_factory = repo_factory or (RepositoryFactory(db) if db else None)
        
        self._password_service: IPasswordService = None
        self._metadata_provider = metadata_provider

    def create_password_service(self) -> IPasswordService:
        if not self._password_service:
            self._password_service = PasswordService()
        return self._password_service

    def create_auth_service(self) -> IAuthService:
        return AuthService(
            user_repo=self._repo_factory.create_user_repository(),
            password_service=self.create_password_service()
        )

    def create_user_service(self) -> IUserService:
        return UserService(
            user_repo=self._repo_factory.create_user_repository()
        )

    def create_registration_service(self) -> IRegistrationService:
        return RegistrationService(
            user_repo=self._repo_factory.create_user_repository(),
            password_service=self.create_password_service()
        )

    def create_token_service(self) -> ITokenService:
        return TokenService(
            user_repo=self._repo_factory.create_user_repository()
        )

    def create_book_catalog_service(self) -> IBookCatalogService:
        return BookCatalogService(
            book_repo=self._repo_factory.create_book_repository()
        )

    def create_library_management_service(self) -> ILibraryManagementService:
        return LibraryManagementService(
            user_book_repo=self._repo_factory.create_user_book_repository(),
            book_repo=self._repo_factory.create_book_repository()
        )

    def create_community_book_service(self) -> ICommunityBookService:
        return CommunityBookService(
            user_book_repo=self._repo_factory.create_user_book_repository(),
            book_repo=self._repo_factory.create_book_repository(),
            user_repo=self._repo_factory.create_user_repository()
        )

    def create_book_import_service(self) -> IBookImportService:
        provider = self._metadata_provider or GoogleBooksProvider()
        
        return BookImportService(
            book_repo=self._repo_factory.create_book_repository(),
            metadata_provider=provider
        )

    def create_loan_service(self) -> ILoanService:
        return LoanService(
            loan_repo=self._repo_factory.create_loan_repository()
        )

    def create_loan_request_service(self) -> ILoanRequestService:
        message_service = self.create_message_service()
        return LoanRequestService(
            request_repo=self._repo_factory.create_loan_request_repository(),
            loan_repo=self._repo_factory.create_loan_repository(),
            user_book_repo=self._repo_factory.create_user_book_repository(),
            message_service=message_service
        )

    def create_message_service(self) -> IMessageService:
        return MessageService(
            message_repo=self._repo_factory.create_message_repository(),
            request_repo=self._repo_factory.create_loan_request_repository(),
            user_book_repo=self._repo_factory.create_user_book_repository()
        )
