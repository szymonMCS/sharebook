import logging
from uuid import UUID
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from src.api.deps import (
    get_loan_service,
    get_current_active_user,
    verify_csrf_protection
)
from src.services.interfaces import ILoanService
from src.schemas.loan import LoanResponse
from src.core.exceptions import ShareBookException
from database.models import User

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/loans", tags=["loans"])


@router.get("/borrowed", response_model=dict)
async def get_my_borrowed_books(
    status: Optional[str] = Query(None, description="Filter by status: active, returned, overdue"),
    loan_service: ILoanService = Depends(get_loan_service),
    current_user: User = Depends(get_current_active_user)
):
    try:
        loans = await loan_service.get_borrowed_books(borrower_id=current_user.id, status=status)

        return {
            "success": True,
            "total": len(loans),
            "loans": loans
        }

    except Exception as e:
        logger.exception("Error fetching borrowed books")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/lent", response_model=dict)
async def get_my_lent_books(
    status: Optional[str] = Query(None, description="Filter by status: active, returned, overdue"),
    loan_service: ILoanService = Depends(get_loan_service),
    current_user: User = Depends(get_current_active_user)
):
    try:
        loans = await loan_service.get_lent_books(lender_id=current_user.id, status=status)

        return {
            "success": True,
            "total": len(loans),
            "loans": loans
        }

    except Exception as e:
        logger.exception("Error fetching lent books")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/borrow-status", response_model=dict)
async def can_borrow_status(loan_service: ILoanService = Depends(get_loan_service), current_user: User = Depends(get_current_active_user)):
    try:
        can_borrow = await loan_service.can_borrow_more(current_user.id)
        active_count = await loan_service.count_active_loans(current_user.id)

        return {
            "success": True,
            "data": {
                "can_borrow": can_borrow,
                "active_loans": active_count,
                "max_loans": 5
            }
        }

    except Exception as e:
        logger.exception("Error checking borrow status")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while checking borrow status"
        )

@router.get("/{loan_id}", response_model=dict)
async def get_loan_details(loan_id: UUID, loan_service: ILoanService = Depends(get_loan_service), current_user: User = Depends(get_current_active_user)):
    try:
        loan = await loan_service.get_loan_by_id(loan_id)

        if not loan:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Loan not found"
            )

        if loan.borrower_id != current_user.id and loan.lender_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this loan"
            )

        return {
            "success": True,
            "data": loan
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Error fetching loan details")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while fetching loan details"
        )

@router.post("/{loan_id}/return", response_model=dict)
async def return_book(loan_id: UUID, loan_service: ILoanService = Depends(get_loan_service), current_user: User = Depends(verify_csrf_protection)):
    try:
        loan = await loan_service.return_book(loan_id=loan_id, user_id=current_user.id)

        return {
            "success": True,
            "message": "Book returned successfully",
            "loan": LoanResponse.model_validate(loan)
        }

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except ShareBookException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        logger.exception("Error returning book")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while returning the book"
        )
