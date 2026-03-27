import logging
from typing import Optional, List
from uuid import UUID
from src.services.interfaces.loans import ILoanService
from database.interfaces import ILoanRepository, IUserRepository, IUserBookRepository
from database.models import Loan
from src.core.exceptions import (
    LoanNotFoundException, 
    NotAuthorizedException, 
    UserNotFoundException,
    BookNotFoundException,
    ValidationException
)
from src.core.constants import LOAN_DURATION_DAYS, MAX_ACTIVE_LOANS
from src.schemas.loan import LoanResponse, BorrowedBookResponse, LentBookResponse, LentBookResponse as LentBookSchema, BookInfo, PersonInfo

logger = logging.getLogger(__name__)


class LoanService(ILoanService):
    def __init__(self, loan_repo: ILoanRepository, user_repo: IUserRepository, user_book_repo: Optional[IUserBookRepository] = None):
        self._loan_repo = loan_repo
        self._user_repo = user_repo
        self._user_book_repo = user_book_repo

    def _validate_borrower_exists(self, user: Optional[object], borrower_id: UUID) -> None:
        if not user:
            raise UserNotFoundException(borrower_id)

    def _validate_loan_limit(self, active_count: int, borrower_id: UUID) -> None:
        if active_count >= MAX_ACTIVE_LOANS:
            raise ValueError(f"Maximum {MAX_ACTIVE_LOANS} active loans")

    async def create_loan(self, user_book_id: UUID, borrower_id: UUID, lender_id: UUID) -> LoanResponse:
        user = await self._user_repo.get_by_id_for_update(borrower_id)
        self._validate_borrower_exists(user, borrower_id)
        active_count = await self._loan_repo.count_active_for_borrower(borrower_id)
        self._validate_loan_limit(active_count, borrower_id)
        loan = await self._loan_repo.create(
            user_book_id=user_book_id,
            borrower_id=borrower_id,
            lender_id=lender_id,
            loan_duration_days=LOAN_DURATION_DAYS
        )

        logger.info(f"Created loan: {loan.id}")
        return LoanResponse.model_validate(loan)

    async def borrow_book(self, user_id: UUID, user_book_id: UUID) -> LoanResponse:
        active_count = await self._loan_repo.count_active_for_borrower(user_id)
        if active_count >= MAX_ACTIVE_LOANS:
            raise ValueError(f"Maximum {MAX_ACTIVE_LOANS} active loans allowed")
        
        user = await self._user_repo.get_by_id_for_update(user_id)
        self._validate_borrower_exists(user, user_id)
        
        if self._user_book_repo:
            user_book = await self._user_book_repo.get_by_id_for_update(user_book_id)
            if not user_book:
                raise BookNotFoundException(user_book_id)
            if user_book.status != "available":
                raise ValidationException("Book is not available for borrowing")
            if not user_book.is_lendable:
                raise ValidationException("This book is not available for lending")
            if user_book.user_id == user_id:
                raise ValidationException("Cannot borrow your own book")
            lender_id = user_book.user_id
        else:
            raise ValueError("UserBook repository required for borrow_book. Use create_loan instead.")
        
        loan = await self._loan_repo.create(
            user_book_id=user_book_id,
            borrower_id=user_id,
            lender_id=lender_id,
            loan_duration_days=LOAN_DURATION_DAYS
        )
        await self._user_book_repo.update_status(user_book_id, "borrowed")
        logger.info(f"Book borrowed: {user_book_id} by user {user_id}, loan {loan.id}")
        return LoanResponse.model_validate(loan)

    async def return_book(self, loan_id: UUID, user_id: UUID) -> LoanResponse:
        loan = await self._loan_repo.get_by_id(loan_id)
        if not loan:
            raise LoanNotFoundException(loan_id)
        if loan.borrower_id != user_id and loan.lender_id != user_id:
            raise NotAuthorizedException("Not authorized to return this loan")
        if loan.status == "returned":
            return LoanResponse.model_validate(loan)
        updated_loan = await self._loan_repo.mark_returned(loan_id)
        
        if self._user_book_repo:
            await self._user_book_repo.update_status(loan.user_book_id, "available")
            logger.info(f"Book {loan.user_book_id} status updated to available")
        
        logger.info(f"Returned loan: {loan_id}")
        return LoanResponse.model_validate(updated_loan)

    async def get_user_loans(self, user_id: UUID) -> List[LoanResponse]:
        borrowed = await self._loan_repo.get_borrower_loans(user_id, status="active")
        lent = await self._loan_repo.get_lender_loans(user_id, status="active")
        all_loans = borrowed + lent
        return [LoanResponse.model_validate(loan) for loan in all_loans]

    async def get_loan(self, loan_id: UUID) -> LoanResponse:
        loan = await self._loan_repo.get_by_id(loan_id)
        if not loan:
            raise LoanNotFoundException(loan_id)
        return LoanResponse.model_validate(loan)

    async def get_borrowed_books(self, borrower_id: UUID, status: Optional[str] = None) -> List[BorrowedBookResponse]:
        loans = await self._loan_repo.get_borrower_loans_with_details(borrower_id, status)
        result = []
        for loan in loans:
            user_book = loan.user_book
            book = user_book.book if user_book else None
            lender = loan.lender
            result.append(BorrowedBookResponse(
                id=loan.id,
                borrowed_at=loan.loan_date,
                due_date=loan.due_date,
                book=BookInfo(
                    id=book.id if book else user_book.book_id if user_book else loan.user_book_id,
                    title=book.title if book else "Unknown",
                    author=book.author if book else None,
                    cover_url=f"/covers/{book.isbn}.jpg" if book and book.isbn else None
                ),
                owner=PersonInfo(
                    id=loan.lender_id,
                    name=f"{lender.first_name} {lender.last_name}" if lender else "Unknown",
                    location=lender.location if lender else None
                )
            ))
        return result

    async def get_lent_books(self, lender_id: UUID, status: Optional[str] = None) -> List[LentBookSchema]:
        loans = await self._loan_repo.get_lender_loans_with_details(lender_id, status)
        result = []
        for loan in loans:
            user_book = loan.user_book
            book = user_book.book if user_book else None
            borrower = loan.borrower
            result.append(LentBookSchema(
                id=loan.id,
                borrowed_at=loan.loan_date,
                due_date=loan.due_date,
                book=BookInfo(
                    id=book.id if book else user_book.book_id if user_book else loan.user_book_id,
                    title=book.title if book else "Unknown",
                    author=book.author if book else None,
                    cover_url=f"/covers/{book.isbn}.jpg" if book and book.isbn else None
                ),
                owner=PersonInfo(
                    id=loan.borrower_id,
                    name=f"{borrower.first_name} {borrower.last_name}" if borrower else "Unknown",
                    location=borrower.location if borrower else None
                )
            ))
        return result

    async def can_borrow_more(self, borrower_id: UUID) -> bool:
        active_count = await self._loan_repo.count_active_for_borrower(borrower_id)
        return active_count < MAX_ACTIVE_LOANS

    async def get_loan_by_id(self, loan_id: UUID) -> Optional[LoanResponse]:
        loan = await self._loan_repo.get_by_id(loan_id)
        return LoanResponse.model_validate(loan) if loan else None

    async def count_active_loans(self, borrower_id: UUID) -> int:
        return await self._loan_repo.count_active_for_borrower(borrower_id)

    async def delete_loan(self, loan_id: UUID) -> bool:
        return await self._loan_repo.delete(loan_id)
