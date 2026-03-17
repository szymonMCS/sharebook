import logging
from uuid import UUID
from typing import Optional
from fastapi import APIRouter, Depends, Query
from src.api.deps import get_loan_request_service, get_current_active_user, verify_csrf_protection
from src.services.interfaces.loans import ILoanRequestService
from src.schemas.loan import (
    LoanRequestCreate,
    LoanRequestResponse,
    LoanRequestActionResponse,
    LoanRequestAction,
    LoanRequestUpdate
)
from src.core.exceptions import (
    ValidationException,
    LoanRequestNotFoundException,
    NotAuthorizedException,
    InvalidLoanRequestStatusException
)
from database.models import User

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/loan-requests", tags=["loan-requests"])

@router.post("", response_model=LoanRequestActionResponse)
async def create_loan_request(
    request_data: LoanRequestCreate,
    loan_request_service: ILoanRequestService = Depends(get_loan_request_service),
    current_user: User = Depends(verify_csrf_protection)
):
    logger.info(f"[DEBUG] Create loan request - user: {current_user.id}, data: {request_data}")
    request = await loan_request_service.create_request(
        user_book_id=request_data.user_book_id,
        requester_id=current_user.id,
        message=request_data.message
    )
    return LoanRequestActionResponse(
        success=True,
        message="Loan request created successfully",
        data=request
    )

@router.get("/incoming", response_model=dict)
async def get_incoming_requests(
    status: Optional[str] = Query(None, description="Filter by status: pending, accepted, rejected, cancelled"),
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(20, ge=1, le=100, description="Items per page"),
    loan_request_service: ILoanRequestService = Depends(get_loan_request_service),
    current_user: User = Depends(get_current_active_user)
):
    skip = (page - 1) * per_page
    requests, total = await loan_request_service.get_incoming_requests(owner_id=current_user.id, status=status, skip=skip, limit=per_page)
    return {
        "success": True,
        "data": requests,
        "meta": {
            "pagination": {
                "page": page,
                "per_page": per_page,
                "total": total,
                "total_pages": (total + per_page - 1) // per_page if per_page > 0 else 0
            }
        }
    }

@router.get("/outgoing", response_model=dict)
async def get_outgoing_requests(
    status: Optional[str] = Query(None, description="Filter by status: pending, accepted, rejected, cancelled"),
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(20, ge=1, le=100, description="Items per page"),
    include_summary: bool = Query(False, description="Include summary counts"),
    loan_request_service: ILoanRequestService = Depends(get_loan_request_service),
    current_user: User = Depends(get_current_active_user)
):
    skip = (page - 1) * per_page
    requests, total = await loan_request_service.get_outgoing_requests(requester_id=current_user.id, status=status, skip=skip, limit=per_page)
    response = {
        "success": True,
        "data": requests,
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
        summary = await loan_request_service.get_summary(current_user.id)
        response["summary"] = summary
    return response

@router.get("/{request_id}", response_model=dict)
async def get_request_details(
    request_id: UUID,
    loan_request_service: ILoanRequestService = Depends(get_loan_request_service),
    current_user: User = Depends(get_current_active_user)
):
    request = await loan_request_service.get_by_id(request_id)
    if not request:
        raise LoanRequestNotFoundException(request_id)
    if request.requester_id != current_user.id and request.owner_id != current_user.id:
        raise NotAuthorizedException("Access denied to this request")
    return {
        "success": True, 
        "data": request
    }

@router.patch("/{request_id}", response_model=LoanRequestActionResponse)
async def update_loan_request(
    request_id: UUID,
    action_data: LoanRequestAction,
    loan_request_service: ILoanRequestService = Depends(get_loan_request_service),
    current_user: User = Depends(verify_csrf_protection)
):
    if action_data.action == "accept":
        request = await loan_request_service.accept_request(request_id=request_id, owner_id=current_user.id)
        return LoanRequestActionResponse(
            success=True,
            message="Request accepted. Book has been loaned.",
            data=request
        )
    elif action_data.action == "reject":
        request = await loan_request_service.reject_request(request_id=request_id, owner_id=current_user.id, reason=action_data.reason)
        return LoanRequestActionResponse(
            success=True,
            message="Request rejected",
            data=request
        )
    else:
        raise ValidationException(f"Unsupported action: {action_data.action}")

@router.patch("/{request_id}/message", response_model=LoanRequestResponse)
async def update_loan_request_message(
    request_id: UUID,
    update_data: LoanRequestUpdate,
    current_user: User = Depends(get_current_active_user),
    loan_request_service: ILoanRequestService = Depends(get_loan_request_service),
):
    request = await loan_request_service.get_by_id(request_id)
    if not request:
        raise LoanRequestNotFoundException(request_id)
    if request.requester_id != current_user.id:
        raise NotAuthorizedException("Only the requester can update this request")
    if request.status != "pending":
        raise InvalidLoanRequestStatusException("Can only update pending requests")
    updated = await loan_request_service.update(request_id, update_data.model_dump(exclude_unset=True))
    return LoanRequestResponse.model_validate(updated)

@router.delete("/{request_id}", response_model=dict)
async def cancel_loan_request(
    request_id: UUID,
    loan_request_service: ILoanRequestService = Depends(get_loan_request_service),
    current_user: User = Depends(verify_csrf_protection)
):
    success = await loan_request_service.cancel_request(request_id=request_id, requester_id=current_user.id)
    if not success:
        raise ValidationException("Cannot cancel request")
    return {
        "success": True, 
        "message": "Request cancelled"
    }
