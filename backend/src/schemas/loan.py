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


class BookInfo(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    
    id: UUID
    title: str
    author: Optional[str] = None
    cover_url: Optional[str] = None


class PersonInfo(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    
    id: UUID
    name: str
    location: Optional[str] = None


class BorrowedBookResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True, from_attributes=True)
    
    id: UUID
    borrowed_at: datetime
    due_date: datetime
    book: BookInfo
    owner: PersonInfo 
    
    @computed_field
    @property
    def days_remaining(self) -> int:
        today = date.today()
        due = self.due_date.date() if isinstance(self.due_date, datetime) else self.due_date
        return (due - today).days


class LentBookResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True, from_attributes=True)
    
    id: UUID 
    borrowed_at: datetime
    due_date: datetime
    book: BookInfo
    owner: PersonInfo 
    
    @computed_field
    @property
    def days_remaining(self) -> int:
        today = date.today()
        due = self.due_date.date() if isinstance(self.due_date, datetime) else self.due_date
        return (due - today).days


class LoanRequestBase(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    message: Optional[str] = Field(None, max_length=1000, description="Wiadomosc od proszacego")


class LoanRequestCreate(LoanRequestBase):
    user_book_id: UUID = Field(..., description="ID książki użytkownika do wypożyczenia")


class LoanRequestResponse(LoanRequestBase):
    model_config = ConfigDict(populate_by_name=True, from_attributes=True)

    id: UUID
    user_book_id: UUID
    book_id: Optional[UUID] = None
    book_title: str = "Unknown"
    book_cover_url: Optional[str] = None
    requester_id: UUID
    requester_name: str = "Unknown"
    requester_avatar: Optional[str] = None
    owner_id: UUID
    owner_name: str = "Unknown"
    owner_avatar: Optional[str] = None
    status: LoanRequestStatus = Field(..., description=f"Status prosby: {', '.join(s.value for s in LoanRequestStatus)}")
    rejection_reason: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    responded_at: Optional[datetime] = None


class LoanRequestActionResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    success: bool
    message: str
    data: Optional[LoanRequestResponse] = None


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
    sender_name: str
    sender_avatar: Optional[str] = None 
    content: str
    message_type: MessageType = Field(..., description=f"Typ wiadomości: {', '.join(t.value for t in MessageType)}")
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
