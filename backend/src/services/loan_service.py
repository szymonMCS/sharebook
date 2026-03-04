import logging
from typing import Optional, List
from uuid import UUID
from src.services.interfaces import ILoanService
from database.interfaces import ILoanRepository
from database.models import Loan
from src.core.exceptions import BookNotFoundException, NotAuthorizedException
from src.core.constants import LOAN_DURATION_DAYS, MAX_ACTIVE_LOANS

logger = logging.getLogger(__name__)


class LoanService(ILoanService):
    def __init__(self, loan_repo: ILoanRepository):
        self._loan_repo = loan_repo

    async def create_loan(self, user_book_id: UUID, borrower_id: UUID, lender_id: UUID) -> Loan:
        if not await self.can_borrow_more(borrower_id):
            raise ValueError("User has reached the maximum number of active loans")

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
            raise BookNotFoundException(loan_id)

        if loan.borrower_id != user_id and loan.lender_id != user_id:
            raise NotAuthorizedException("Not authorized to return this loan")

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
