from pydantic import BaseModel, Field, ConfigDict, computed_field
from datetime import datetime, date
from uuid import UUID
from typing import Optional, List
from src.core.constants import LoanStatus, LoanRequestStatus, MessageType


class LoanBase(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    status: LoanStatus = Field(
        default=LoanStatus.ACTIVE,
        description=f"Status wypozyczenia: {', '.join(s.value for s in LoanStatus)}"
    )


class LoanResponse(LoanBase):
    model_config = ConfigDict(populate_by_name=True, from_attributes=True)

    id: UUID
    user_book_id: UUID
    borrower_id: UUID
    lender_id: UUID
    loan_date: datetime
    due_date: datetime
    return_date: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime


class BorrowedBookResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True, from_attributes=True)
    
    loan_id: UUID
    borrowed_at: datetime
    due_date: datetime
    
    # Denormalizacja - dane książki
    book_id: UUID
    book_title: str
    book_author: Optional[str] = None
    book_cover_url: Optional[str] = None
    
    # Denormalizacja - dane właściciela (lender)
    lender_id: UUID
    lender_name: str
    lender_location: Optional[str] = None
    
    @computed_field
    @property
    def days_remaining(self) -> int:
        today = date.today()
        due = self.due_date.date() if isinstance(self.due_date, datetime) else self.due_date
        return (due - today).days


class LentBookResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True, from_attributes=True)
    
    loan_id: UUID
    borrowed_at: datetime
    due_date: datetime
    
    # Denormalizacja - dane książki
    book_id: UUID
    book_title: str
    book_author: Optional[str] = None
    
    # Denormalizacja - dane pożyczającego (borrower)
    borrower_id: UUID
    borrower_name: str
    borrower_location: Optional[str] = None
    
    @computed_field
    @property
    def days_remaining(self) -> int:
        today = date.today()
        due = self.due_date.date() if isinstance(self.due_date, datetime) else self.due_date
        return (due - today).days


class LoanRequestBase(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    message: Optional[str] = Field(
        None,
        max_length=1000,
        description="Wiadomosc od proszacego"
    )


class LoanRequestCreate(LoanRequestBase):
    user_book_id: UUID = Field(..., description="ID książki użytkownika do wypożyczenia")


class LoanRequestResponse(LoanRequestBase):
    model_config = ConfigDict(populate_by_name=True, from_attributes=True)

    id: UUID
    user_book_id: UUID
    requester_id: UUID
    owner_id: UUID
    status: LoanRequestStatus = Field(
        ...,
        description=f"Status prosby: {', '.join(s.value for s in LoanRequestStatus)}"
    )
    rejection_reason: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class LoanRequestActionResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    success: bool
    message: str
    request: Optional[LoanRequestResponse] = None


class RejectRequestRequest(BaseModel):
    reason: Optional[str] = Field(
        None,
        max_length=500,
        description="Powod odrzucenia"
    )


class LoanRequestAction(BaseModel):
    action: str = Field(..., pattern="^(accept|reject)$", description="Akcja do wykonania: accept lub reject")
    reason: Optional[str] = Field(None, max_length=500, description="Powód odrzucenia (wymagany tylko dla action=reject)")


class LoanRequestUpdate(BaseModel):
    message: Optional[str] = Field(None, max_length=1000, description="Nowa wiadomość do właściciela książki")


class LoanUpdate(BaseModel):
    status: str = Field(..., pattern="^(returned)$", description="Nowy status wypożyczenia: returned")


class LoanRequestsSummary(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    incoming_pending: int
    outgoing_pending: int


class MessageCreate(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    content: str = Field(..., min_length=1, max_length=2000, description="Treść wiadomości")


class MessageResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True, from_attributes=True)
    
    id: UUID
    loan_request_id: UUID
    sender_id: UUID
    sender_name: str  # Denormalizacja
    sender_avatar: Optional[str] = None  # Denormalizacja
    content: str
    message_type: MessageType = Field(
        ...,
        description=f"Typ wiadomości: {', '.join(t.value for t in MessageType)}"
    )
    is_read: bool
    created_at: datetime
    updated_at: datetime


class MessageThreadResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True, from_attributes=True)
    
    loan_request_id: UUID
    user_book_id: UUID
    book_title: str
    status: str
    messages: List[MessageResponse]
    total_messages: int
    unread_count: int
