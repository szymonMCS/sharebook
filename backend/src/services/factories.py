from functools import lru_cache
from sqlalchemy.ext.asyncio import AsyncSession
from src.services.interfaces.factory import IRepositoryFactory, IServiceFactory
from src.services.interfaces.auth import (
    IAuthService,
    IUserService,
    IRegistrationService,
    ITokenService,
    IPasswordService,
)
from src.services.interfaces.books import (
    IBookCatalogService,
    ILibraryManagementService,
    ICommunityBookService,
    IBookImportService,
    IBookMetadataProvider,
)
from src.services.interfaces.loans import ILoanService, ILoanRequestService
from src.services.interfaces.messages import IMessageService
from database.repositories.user_repository import UserRepository
from database.repositories.book_repository import BookRepository
from database.repositories.user_book_repository import UserBookRepository
from database.repositories.loan_repository import LoanRepository
from database.repositories.loan_request_repository import LoanRequestRepository
from database.repositories.message_repository import MessageRepository
from database.repositories.book_chunk_repository import BookChunkRepository
from src.services.auth import AuthService, RegistrationService, TokenService, PasswordService
from src.services.users import UserService
from src.services.books import BookCatalogService, LibraryManagementService, CommunityBookService, BookImportService
from src.services.loans import LoanService, LoanRequestService
from src.services.messages import MessageService
from src.services.google_books_provider import GoogleBooksProvider
from src.services.admin import AdminDashboardService, UserAdminService, BookAdminService
from src.services.ai import PgVectorSearchService, BookIndexingService, OpenAIEmbeddingService, SmartChunkingStrategy
from src.services.cover import (
            CoverManager,
            OpenLibrarySource,
            GoogleBooksSource,
            AICoverSource,
            SequentialSourceStrategy,
            CoverStorage,
        )
from src.services.enrichment import (
            EnrichmentOrchestrator,
            GoogleBooksAdapter,
            OpenAIAdapter,
            DefaultEnrichmentStrategy,
        )
from src.services.sagas import (
            SagaOrchestrator,
            ValidateRequestStep,
            CreateLoanStep,
            UpdateBookStatusStep,
            AcceptRequestStep,
        )


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
    def create_book_chunk_repository(self):
        return BookChunkRepository(self._db)


class ServiceFactory(IServiceFactory):
    def __init__(
        self, 
        db: AsyncSession = None, 
        repo_factory: IRepositoryFactory = None,
        metadata_provider: IBookMetadataProvider = None
    ):
        self._db = db
        self._repo_factory = repo_factory or (RepositoryFactory(db) if db else None)
        self._metadata_provider = metadata_provider

    @lru_cache(maxsize=1)
    def create_password_service(self) -> IPasswordService:
        return PasswordService()
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
            book_repo=self._repo_factory.create_book_repository(),
            db=self._db
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
            loan_repo=self._repo_factory.create_loan_repository(),
            user_repo=self._repo_factory.create_user_repository()
        )
    def create_loan_request_service(self) -> ILoanRequestService:
        message_service = self.create_message_service()
        return LoanRequestService(
            request_repo=self._repo_factory.create_loan_request_repository(),
            loan_repo=self._repo_factory.create_loan_repository(),
            user_book_repo=self._repo_factory.create_user_book_repository(),
            message_service=message_service,
            db=self._db
        )
    def create_message_service(self) -> IMessageService:
        return MessageService(
            message_repo=self._repo_factory.create_message_repository(),
            request_repo=self._repo_factory.create_loan_request_repository(),
            user_book_repo=self._repo_factory.create_user_book_repository()
        )
    def create_cover_service(self):
        return CoverManager(
            sources=[
                OpenLibrarySource(),
                GoogleBooksSource(),
                AICoverSource(),
            ],
            strategy=SequentialSourceStrategy(),
            storage=CoverStorage()
        )
    def create_admin_dashboard_service(self):
        return AdminDashboardService(
            user_repo=self._repo_factory.create_user_repository(),
            book_repo=self._repo_factory.create_book_repository(),
            loan_repo=self._repo_factory.create_loan_repository(),
            user_book_repo=self._repo_factory.create_user_book_repository()
        )
    def create_user_admin_service(self):
        return UserAdminService(
            db=self._db,
            user_repo=self._repo_factory.create_user_repository(),
            user_book_repo=self._repo_factory.create_user_book_repository(),
            loan_repo=self._repo_factory.create_loan_repository()
        )
    def create_book_admin_service(self):
        return BookAdminService(
            db=self._db,
            book_repo=self._repo_factory.create_book_repository(),
            user_book_repo=self._repo_factory.create_user_book_repository(),
            loan_repo=self._repo_factory.create_loan_repository()
        )
    def create_embedding_service(self):
        return OpenAIEmbeddingService()
    def create_vector_search_service(self):
        return PgVectorSearchService(
            chunk_repo=BookChunkRepository(self._db),
            embedding_service=OpenAIEmbeddingService()
        )

    def create_book_indexing_service(self):
        return BookIndexingService(
            book_repo=self._repo_factory.create_book_repository(),
            chunk_repo=BookChunkRepository(self._db),
            embedding_service=OpenAIEmbeddingService(),
            chunking_strategy=SmartChunkingStrategy()
        )

    def create_cover_manager(self):
        return CoverManager(
            sources=[OpenLibrarySource(), GoogleBooksSource(), AICoverSource(),],
            strategy=SequentialSourceStrategy(),
            storage=CoverStorage()
        )

    def create_enrichment_orchestrator(self):
        return EnrichmentOrchestrator(
            db=self._db,
            adapters=[GoogleBooksAdapter(),OpenAIAdapter(),],
            strategy=DefaultEnrichmentStrategy(),
        )

    def create_loan_acceptance_saga(self):
        loan_service = self.create_loan_service()
        request_service = self.create_loan_request_service()
        return SagaOrchestrator(
            steps=[ValidateRequestStep(request_service=request_service, loan_service=loan_service),
                CreateLoanStep(loan_service=loan_service,request_service=request_service),
                UpdateBookStatusStep(library_service=self.create_library_management_service()),
                AcceptRequestStep(request_service=request_service),
            ]
        )
