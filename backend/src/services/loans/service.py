import logging
from typing import Optional, List
from uuid import UUID
from src.services.interfaces.loans import ILoanService
from database.interfaces import ILoanRepository, IUserRepository
from database.models import Loan
from src.core.exceptions import LoanNotFoundException, NotAuthorizedException, UserNotFoundException
from src.core.constants import LOAN_DURATION_DAYS, MAX_ACTIVE_LOANS

logger = logging.getLogger(__name__)


class LoanService(ILoanService):
    def __init__(self, loan_repo: ILoanRepository, user_repo: IUserRepository):
        self._loan_repo = loan_repo
        self._user_repo = user_repo

    def _validate_borrower_exists(self, user: Optional[object], borrower_id: UUID) -> None:
        if not user:
            raise UserNotFoundException(borrower_id)

    def _validate_loan_limit(self, active_count: int, borrower_id: UUID) -> None:
        if active_count >= MAX_ACTIVE_LOANS:
            raise ValueError(f"Maximum {MAX_ACTIVE_LOANS} active loans")

    async def create_loan(self, user_book_id: UUID, borrower_id: UUID, lender_id: UUID) -> Loan:
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
        return loan

    async def return_book(self, loan_id: UUID, user_id: UUID) -> Loan:
        loan = await self._loan_repo.get_by_id(loan_id)
        if not loan:
            raise LoanNotFoundException(loan_id)

        if loan.borrower_id != user_id and loan.lender_id != user_id:
            raise NotAuthorizedException("Not authorized to return this loan")

        if loan.status == "returned":
            return loan

        updated_loan = await self._loan_repo.mark_returned(loan_id)

        logger.info(f"Returned loan: {loan_id}")
        return updated_loan

    async def get_borrowed_books(self, borrower_id: UUID, status: Optional[str] = None) -> List[Loan]:
        loans = await self._loan_repo.get_borrower_loans(borrower_id, status)
        return loans

    async def get_lent_books(self, lender_id: UUID, status: Optional[str] = None) -> List[Loan]:
        loans = await self._loan_repo.get_lender_loans(lender_id, status)
        return loans

    async def can_borrow_more(self, borrower_id: UUID) -> bool:
        active_count = await self._loan_repo.count_active_for_borrower(borrower_id)
        return active_count < MAX_ACTIVE_LOANS

    async def get_loan_by_id(self, loan_id: UUID) -> Optional[Loan]:
        return await self._loan_repo.get_by_id(loan_id)

    async def count_active_loans(self, borrower_id: UUID) -> int:
        return await self._loan_repo.count_active_for_borrower(borrower_id)

    async def delete_loan(self, loan_id: UUID) -> bool:
        return await self._loan_repo.delete(loan_id)
