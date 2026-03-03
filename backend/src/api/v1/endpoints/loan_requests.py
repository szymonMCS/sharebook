import logging
from uuid import UUID
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from src.api.deps import (
    get_loan_request_service,
    get_loan_service,
    get_library_management_service,
    get_message_service,
    get_current_active_user,
    verify_csrf_protection
)
from src.services.interfaces import (
    ILoanRequestService,
    ILoanService,
    ILibraryManagementService,
    IMessageService,
)
from src.services.sagas.loan_acceptance_saga import LoanAcceptanceSaga
from src.schemas.loan import (
    LoanRequestCreate,
    LoanRequestResponse,
    LoanRequestActionResponse,
    RejectRequestRequest,
    LoanRequestsSummary
)
from src.core.exceptions import ShareBookException
from database.models import User

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/loan-requests", tags=["loan-requests"])


@router.post("", response_model=LoanRequestActionResponse, status_code=status.HTTP_201_CREATED)
async def create_loan_request(
    request_data: LoanRequestCreate,
    user_book_id: UUID,
    loan_request_service: ILoanRequestService = Depends(get_loan_request_service),
    current_user: User = Depends(verify_csrf_protection)
):
    try:
        request = await loan_request_service.create_request(
            user_book_id=user_book_id,
            requester_id=current_user.id,
            message=request_data.message
        )

        return LoanRequestActionResponse(
            success=True,
            message="Loan request created successfully",
            request=LoanRequestResponse.model_validate(request)
        )

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except ShareBookException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        logger.exception("Error creating loan request")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while creating the loan request"
        )


@router.get("/incoming", response_model=dict)
async def get_incoming_requests(
    status: Optional[str] = Query(None, description="Filter by status: pending, accepted, rejected, cancelled"),
    loan_request_service: ILoanRequestService = Depends(get_loan_request_service),
    current_user: User = Depends(get_current_active_user)
):
    try:
        requests = await loan_request_service.get_incoming_requests(
            owner_id=current_user.id,
            status=status
        )

        return {
            "success": True,
            "total": len(requests),
            "requests": requests
        }

    except Exception as e:
        logger.exception("Error fetching incoming requests")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while fetching incoming requests"
        )


@router.get("/outgoing", response_model=dict)
async def get_outgoing_requests(
    status: Optional[str] = Query(None, description="Filter by status: pending, accepted, rejected, cancelled"),
    loan_request_service: ILoanRequestService = Depends(get_loan_request_service),
    current_user: User = Depends(get_current_active_user)
):
    try:
        requests = await loan_request_service.get_outgoing_requests(
            requester_id=current_user.id,
            status=status
        )

        return {
            "success": True,
            "total": len(requests),
            "requests": requests
        }

    except Exception as e:
        logger.exception("Error fetching outgoing requests")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while fetching outgoing requests"
        )


@router.get("/summary", response_model=LoanRequestsSummary)
async def get_requests_summary(
    loan_request_service: ILoanRequestService = Depends(get_loan_request_service),
    current_user: User = Depends(get_current_active_user)
):
    try:
        summary = await loan_request_service.get_summary(current_user.id)
        return LoanRequestsSummary(**summary)

    except Exception as e:
        logger.exception("Error fetching requests summary")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/{request_id}", response_model=dict)
async def get_request_details(
    request_id: UUID,
    loan_request_service: ILoanRequestService = Depends(get_loan_request_service),
    current_user: User = Depends(get_current_active_user)
):
    try:
        request = await loan_request_service.get_request_details(request_id)

        if not request:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Request not found"
            )

        if request.requester_id != current_user.id and request.owner_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this request"
            )

        return {
            "success": True,
            "data": request
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Error fetching request details")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while fetching request details"
        )


@router.patch("/{request_id}/accept", response_model=LoanRequestActionResponse)
async def accept_loan_request(
    request_id: UUID,
    loan_request_service: ILoanRequestService = Depends(get_loan_request_service),
    loan_service: ILoanService = Depends(get_loan_service),
    library_service: ILibraryManagementService = Depends(get_library_management_service),
    message_service: IMessageService = Depends(get_message_service),
    current_user: User = Depends(verify_csrf_protection)
):
    try:
        saga = LoanAcceptanceSaga(
            loan_request_service=loan_request_service,
            loan_service=loan_service,
            library_service=library_service,
            message_service=message_service,
        )
        
        result = await saga.execute(
            request_id=request_id,
            owner_id=current_user.id
        )
        
        if not result.success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result.error_message
            )
        
        request = await loan_request_service.get_request_details(request_id)

        return LoanRequestActionResponse(
            success=True,
            message="Request accepted. Book has been loaned.",
            request=LoanRequestResponse.model_validate(request)
        )

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except ShareBookException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        logger.exception("Error accepting loan request")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while accepting the loan request"
        )


@router.patch("/{request_id}/reject", response_model=LoanRequestActionResponse)
async def reject_loan_request(
    request_id: UUID,
    reject_data: RejectRequestRequest,
    loan_request_service: ILoanRequestService = Depends(get_loan_request_service),
    current_user: User = Depends(verify_csrf_protection)
):
    try:
        request = await loan_request_service.reject_request(
            request_id=request_id,
            owner_id=current_user.id,
            reason=reject_data.reason
        )

        return LoanRequestActionResponse(
            success=True,
            message="Request rejected",
            request=LoanRequestResponse.model_validate(request)
        )

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except ShareBookException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        logger.exception("Error rejecting loan request")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while rejecting the loan request"
        )


@router.delete("/{request_id}", response_model=dict)
async def cancel_loan_request(
    request_id: UUID,
    loan_request_service: ILoanRequestService = Depends(get_loan_request_service),
    current_user: User = Depends(verify_csrf_protection)
):
    try:
        success = await loan_request_service.cancel_request(
            request_id=request_id,
            requester_id=current_user.id
        )

        if success:
            return {
                "success": True,
                "message": "Request cancelled"
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot cancel request"
            )

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except ShareBookException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        logger.exception("Error cancelling loan request")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while cancelling the loan request"
        )
