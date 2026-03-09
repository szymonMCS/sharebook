import logging
from uuid import UUID
from typing import Optional
from fastapi import APIRouter, Depends, Query
from src.api.deps import get_loan_service, get_current_active_user, verify_csrf_protection
from src.services.interfaces.loans import ILoanService
from src.schemas.loan import LoanResponse, LoanUpdate
from src.core.exceptions import ValidationException, NotAuthorizedException, LoanNotFoundException
from src.core.constants import MAX_ACTIVE_LOANS
from database.models import User

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/loans", tags=["loans"])


@router.get("", response_model=dict)
async def get_loans(
    type: Optional[str] = Query(None, description="Filter by type: borrowed, lent"),
    status: Optional[str] = Query(None, description="Filter by status: active, returned, overdue"),
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(20, ge=1, le=100, description="Items per page"),
    include_summary: bool = Query(False, description="Include borrow status summary"),
    loan_service: ILoanService = Depends(get_loan_service),
    current_user: User = Depends(get_current_active_user)
):
    if type == "borrowed":
        loans = await loan_service.get_borrowed_books(borrower_id=current_user.id, status=status)
    elif type == "lent":
        loans = await loan_service.get_lent_books(lender_id=current_user.id, status=status)
    else:
        borrowed = await loan_service.get_borrowed_books(borrower_id=current_user.id, status=status)
        lent = await loan_service.get_lent_books(lender_id=current_user.id, status=status)
        loans = borrowed + lent

    total = len(loans)
    start_idx = (page - 1) * per_page
    end_idx = start_idx + per_page
    paginated_loans = loans[start_idx:end_idx]

    response = {
        "success": True,
        "total": total,
        "loans": paginated_loans,
        "meta": {
            "pagination": {
                "page": page,
                "per_page": per_page,
                "total": total,
                "total_pages": (total + per_page - 1) // per_page if per_page > 0 else 0
            }
        }
    }
    if include_summary:
        can_borrow = await loan_service.can_borrow_more(current_user.id)
        active_count = await loan_service.count_active_loans(current_user.id)
        response["summary"] = {
            "can_borrow": can_borrow,
            "active_loans": active_count,
            "max_loans": MAX_ACTIVE_LOANS
        }
    return response

@router.get("/{loan_id}", response_model=dict)
async def get_loan_details(loan_id: UUID, loan_service: ILoanService = Depends(get_loan_service), current_user: User = Depends(get_current_active_user)):
    loan = await loan_service.get_loan_by_id(loan_id)
    if not loan:
        raise LoanNotFoundException(loan_id)
    if loan.borrower_id != current_user.id and loan.lender_id != current_user.id:
        raise NotAuthorizedException("Access denied to this loan")
    return {
        "success": True, 
        "data": loan
    }

@router.patch("/{loan_id}", response_model=dict)
async def update_loan(
    loan_id: UUID,
    update_data: LoanUpdate,
    loan_service: ILoanService = Depends(get_loan_service),
    current_user: User = Depends(verify_csrf_protection)
):
    if update_data.status == "returned":
        loan = await loan_service.return_book(loan_id=loan_id, user_id=current_user.id)

        return {
            "success": True,
            "message": "Book returned successfully",
            "loan": LoanResponse.model_validate(loan)
        }
    else:
        raise ValidationException(f"Unsupported status update: {update_data.status}")
