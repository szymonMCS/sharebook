from uuid import UUID
from fastapi import APIRouter, Depends
from src.api.deps import get_message_service, get_current_active_user, verify_csrf_protection
from src.services.interfaces.messages import IMessageService
from src.schemas.loan import MessageCreate
from database.models import User

router = APIRouter(prefix="/loan-requests-messages", tags=["messages"])


@router.get("/{request_id}/messages", response_model=dict)
async def get_message_thread(
    request_id: UUID,
    message_service: IMessageService = Depends(get_message_service),
    current_user: User = Depends(get_current_active_user)
):
    thread = await message_service.get_thread(request_id, current_user.id)
    return {"success": True, "data": thread}


@router.post("/{request_id}/messages", response_model=dict)
async def send_message(
    request_id: UUID,
    message_data: MessageCreate,
    message_service: IMessageService = Depends(get_message_service),
    current_user: User = Depends(verify_csrf_protection)
):
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


@router.patch("/messages/{message_id}/read", response_model=dict)
async def mark_message_read(
    message_id: UUID,
    message_service: IMessageService = Depends(get_message_service),
    current_user: User = Depends(verify_csrf_protection)
):
    result = await message_service.mark_message_as_read(
        message_id=message_id,
        user_id=current_user.id
    )
    return {"success": result, "data": None}


@router.post("/{request_id}/messages/read-all", response_model=dict)
async def mark_all_messages_read(
    request_id: UUID,
    message_service: IMessageService = Depends(get_message_service),
    current_user: User = Depends(get_current_active_user)
):
    count = await message_service.mark_all_as_read(
        loan_request_id=request_id,
        user_id=current_user.id
    )
    return {"success": True, "data": {"marked_as_read": count}}
