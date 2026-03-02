from abc import ABC, abstractmethod
from uuid import UUID
from typing import Optional, List
from src.schemas.user import UserCreate, UserUpdate, UserResponse, UserProfileResponse


class IAuthService(ABC):
    @abstractmethod
    async def authenticate(self, email: str, password: str) -> Optional[UserResponse]:
        pass


class IUserService(ABC):
    @abstractmethod
    async def get_by_id(self, user_id: UUID) -> UserResponse:
        pass
    @abstractmethod
    async def get_by_email(self, email: str) -> Optional[UserResponse]:
        pass
    @abstractmethod
    async def exists_by_email(self, email: str) -> bool:
        pass
    @abstractmethod
    async def update(self, user_id: UUID, user_update: UserUpdate) -> UserResponse:
        pass
    @abstractmethod
    async def get_profile(self, user_id: UUID) -> UserProfileResponse:
        pass


class IRegistrationService(ABC):
    @abstractmethod
    async def register(self, user_data: UserCreate) -> UserResponse:
        pass


class IPasswordService(ABC):
    @abstractmethod
    def hash(self, password: str) -> str:
        pass
    @abstractmethod
    def verify(self, plain_password: str, hashed_password: str) -> bool:
        pass


class ITokenService(ABC):
    @abstractmethod
    def generate_token_pair(self, user_id: UUID) -> tuple[str, str, str]:
        pass
    @abstractmethod
    async def refresh_access_token(self, refresh_token: str) -> tuple[str, str]:
        pass
    @abstractmethod
    def decode_token(self, token: str) -> Optional[dict]:
        pass


class IBookCatalogService(ABC):
    @abstractmethod
    async def get_by_id(self, book_id: UUID) -> "BookResponse":
        pass
    @abstractmethod
    async def get_by_isbn(self, isbn: str) -> Optional["BookResponse"]:
        pass
    @abstractmethod
    async def search(self, query: Optional[str] = None, author: Optional[str] = None, genre: Optional[str] = None, skip: int = 0, limit: int = 20) -> tuple[List["BookResponse"], int]:
        pass
    @abstractmethod
    async def create(self, data: "BookCreate") -> "BookResponse":
        pass
    @abstractmethod
    async def update(self, book_id: UUID, data: "BookUpdate") -> "BookResponse":
        pass


class ILibraryManagementService(ABC):
    @abstractmethod
    async def add_book_to_library(self, user_id: UUID, isbn: str, condition: str) -> "UserBookResponse":
        pass
    @abstractmethod
    async def get_library(self, user_id: UUID, skip: int = 0, limit: int = 100) -> List["UserBookResponse"]:
        pass
    @abstractmethod
    async def get_library_item(self, user_id: UUID, user_book_id: UUID) -> Optional["UserBookResponse"]:
        pass
    @abstractmethod
    async def remove_from_library(self, user_id: UUID, user_book_id: UUID) -> bool:
        pass
    @abstractmethod
    async def update_lendable_status(self, user_id: UUID, user_book_id: UUID, is_lendable: bool) -> "UserBookResponse":
        pass
    @abstractmethod
    async def update_status(self, user_id: UUID, user_book_id: UUID, status: str) -> "UserBookResponse":
        pass


class ICommunityBookService(ABC):
    @abstractmethod
    async def get_community_books(
        self,
        exclude_user_id: Optional[UUID] = None,
        status: Optional[str] = None,
        search: Optional[str] = None,
        author: Optional[str] = None,
        skip: int = 0,
        limit: int = 20
    ) -> tuple[List["CommunityBookResponse"], int]:
        pass


class IBookMetadataProvider(ABC):
    @abstractmethod
    async def fetch_by_isbn(self, isbn: str) -> Optional["BookMetadata"]:
        pass
    @abstractmethod
    async def search_by_title(self, title: str, max_results: int = 10) -> List["BookMetadata"]:
        pass


class IMetadataProviderFactory(ABC):
    @abstractmethod
    def create_provider(self) -> IBookMetadataProvider:
        pass


class IBookImportService(ABC):
    @abstractmethod
    async def import_by_isbn(self, isbn: str) -> "BookResponse":
        pass
    @abstractmethod
    async def enrich_book_data(self, book_id: UUID) -> "BookResponse":
        pass
    @abstractmethod
    async def search_and_import(self, query: str, limit: int = 5) -> List["BookResponse"]:
        pass


class BookMetadata:
    def __init__(
        self,
        isbn: str,
        title: str,
        author: str,
        description: Optional[str] = None,
        publisher: Optional[str] = None,
        publication_year: Optional[int] = None,
        page_count: Optional[int] = None,
        language: Optional[str] = None,
        genre: Optional[str] = None,
        cover_url: Optional[str] = None
    ):
        self.isbn = isbn
        self.title = title
        self.author = author
        self.description = description
        self.publisher = publisher
        self.publication_year = publication_year
        self.page_count = page_count
        self.language = language
        self.genre = genre
        self.cover_url = cover_url


# Forward references for type hints
BookResponse = "BookResponse"
BookCreate = "BookCreate"
BookUpdate = "BookUpdate"
UserBookResponse = "UserBookResponse"
CommunityBookResponse = "CommunityBookResponse"
LoanResponse = "LoanResponse"
LoanRequestResponse = "LoanRequestResponse"


class IRepositoryFactory(ABC):
    @abstractmethod
    def create_user_repository(self) -> "IUserRepository":
        pass
    @abstractmethod
    def create_book_repository(self) -> "IBookRepository":
        pass
    @abstractmethod
    def create_user_book_repository(self) -> "IUserBookRepository":
        pass
    @abstractmethod
    def create_loan_repository(self) -> "ILoanRepository":
        pass
    @abstractmethod
    def create_loan_request_repository(self) -> "ILoanRequestRepository":
        pass


class ILoanService(ABC):
    @abstractmethod
    async def create_loan(self, user_book_id: UUID, borrower_id: UUID, lender_id: UUID) -> "LoanResponse":
        pass
    @abstractmethod
    async def return_book(self, loan_id: UUID, user_id: UUID) -> "LoanResponse":
        pass
    @abstractmethod
    async def get_borrowed_books(self, borrower_id: UUID, status: Optional[str] = None) -> List["LoanResponse"]:
        pass
    @abstractmethod
    async def get_lent_books(self, lender_id: UUID, status: Optional[str] = None) -> List["LoanResponse"]:
        pass
    @abstractmethod
    async def can_borrow_more(self, borrower_id: UUID) -> bool:
        pass
    @abstractmethod
    async def get_loan_by_id(self, loan_id: UUID) -> Optional["LoanResponse"]:
        pass
    @abstractmethod
    async def count_active_loans(self, borrower_id: UUID) -> int:
        pass


class ILoanRequestService(ABC):
    @abstractmethod
    async def create_request(self, user_book_id: UUID, requester_id: UUID, message: Optional[str] = None) -> "LoanRequestResponse":
        pass
    @abstractmethod
    async def accept_request(self, request_id: UUID, owner_id: UUID) -> "LoanRequestResponse":
        pass
    @abstractmethod
    async def reject_request(self, request_id: UUID, owner_id: UUID, reason: Optional[str] = None) -> "LoanRequestResponse":
        pass
    @abstractmethod
    async def cancel_request(self, request_id: UUID, requester_id: UUID) -> bool:
        pass
    @abstractmethod
    async def get_incoming_requests(self, owner_id: UUID, status: Optional[str] = "pending") -> List["LoanRequestResponse"]:
        pass
    @abstractmethod
    async def get_outgoing_requests(self,requester_id: UUID, status: Optional[str] = None) -> List["LoanRequestResponse"]:
        pass
    @abstractmethod
    async def get_request_details(self, request_id: UUID) -> Optional["LoanRequestResponse"]:
        pass
    @abstractmethod
    async def get_summary(self, user_id: UUID) -> dict:
        pass


class IServiceFactory(ABC):
    @abstractmethod
    def create_auth_service(self) -> IAuthService:
        pass
    @abstractmethod
    def create_user_service(self) -> IUserService:
        pass
    @abstractmethod
    def create_registration_service(self) -> IRegistrationService:
        pass
    @abstractmethod
    def create_token_service(self) -> ITokenService:
        pass
    @abstractmethod
    def create_password_service(self) -> IPasswordService:
        pass
    @abstractmethod
    def create_book_catalog_service(self) -> IBookCatalogService:
        pass
    @abstractmethod
    def create_library_management_service(self) -> ILibraryManagementService:
        pass
    @abstractmethod
    def create_book_import_service(self) -> IBookImportService:
        pass
    @abstractmethod
    def create_loan_service(self) -> ILoanService:
        pass
    @abstractmethod
    def create_loan_request_service(self) -> ILoanRequestService:
        pass
