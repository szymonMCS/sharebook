import logging
from uuid import UUID
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status

from src.api.deps import get_message_service, get_current_active_user, verify_csrf_protection
from src.services.interfaces import IMessageService
from src.schemas.loan import MessageCreate, MessageResponse, MessageThreadResponse
from src.core.exceptions import ShareBookException, NotAuthorizedException, LoanRequestNotFoundException
from database.models import User

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/loan-requests", tags=["messages"])


@router.get("/{request_id}/messages", response_model=dict)
async def get_message_thread(
    request_id: UUID,
    message_service: IMessageService = Depends(get_message_service),
    current_user: User = Depends(get_current_active_user)
):
    try:
        thread = await message_service.get_thread(request_id, current_user.id)
        return {
            "success": True,
            "data": thread
        }
    except LoanRequestNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Request not found"
        )
    except NotAuthorizedException:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not part of this conversation"
        )
    except Exception as e:
        logger.exception("Error fetching message thread")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.post("/{request_id}/messages", response_model=dict)
async def send_message(
    request_id: UUID,
    message_data: MessageCreate,
    message_service: IMessageService = Depends(get_message_service),
    current_user: User = Depends(verify_csrf_protection)
):
    try:
        message = await message_service.send_message(
            loan_request_id=request_id,
            sender_id=current_user.id,
            content=message_data.content
        )
        return {
            "success": True,
            "data": message,
            "message": "Message sent successfully"
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except NotAuthorizedException as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e)
        )
    except Exception as e:
        logger.exception("Error sending message")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.patch("/messages/{message_id}/read", response_model=dict)
async def mark_message_read(
    message_id: UUID,
    message_service: IMessageService = Depends(get_message_service),
    current_user: User = Depends(get_current_active_user)
):
    try:
        result = await message_service.mark_message_as_read(
            message_id=message_id,
            user_id=current_user.id
        )
        return {
            "success": result,
            "data": None
        }
    except LoanRequestNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Message not found"
        )
    except Exception as e:
        logger.exception("Error marking message as read")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.post("/{request_id}/messages/read-all", response_model=dict)
async def mark_all_messages_read(
    request_id: UUID,
    message_service: IMessageService = Depends(get_message_service),
    current_user: User = Depends(get_current_active_user)
):
    try:
        count = await message_service.mark_all_as_read(
            loan_request_id=request_id,
            user_id=current_user.id
        )
        return {
            "success": True,
            "data": {"marked_as_read": count}
        }
    except NotAuthorizedException:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    except Exception as e:
        logger.exception("Error marking all messages as read")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/messages/unread-count", response_model=dict)
async def get_unread_count(
    message_service: IMessageService = Depends(get_message_service),
    current_user: User = Depends(get_current_active_user)
):
    """
    TODO: Obecnie zwraca 0 - wymaga pełnej implementacji w MessageRepository.
    """
    try:
        count = await message_service.get_total_unread_count(current_user.id)
        return {
            "success": True,
            "data": {"unread_count": count}
        }
    except Exception as e:
        logger.exception("Error fetching unread count")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
