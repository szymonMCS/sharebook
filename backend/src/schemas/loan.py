from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from uuid import UUID
from typing import Optional


class LoanBase(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    status: str = Field(
        default="active",
        pattern="^(active|returned|overdue)$",
        description="Status wypozyczenia"
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


class LoanRequestBase(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    message: Optional[str] = Field(
        None,
        max_length=1000,
        description="Wiadomosc od proszacego"
    )


class LoanRequestCreate(LoanRequestBase):
    pass


class LoanRequestResponse(LoanRequestBase):
    model_config = ConfigDict(populate_by_name=True, from_attributes=True)

    id: UUID
    user_book_id: UUID
    requester_id: UUID
    owner_id: UUID
    status: str = Field(
        ...,
        pattern="^(pending|accepted|rejected|cancelled)$",
        description="Status prosby"
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


class LoanRequestsSummary(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    incoming_pending: int
    outgoing_pending: int
