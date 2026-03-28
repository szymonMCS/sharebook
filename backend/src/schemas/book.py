from pydantic import BaseModel, Field, ConfigDict, field_validator
from datetime import datetime
from uuid import UUID
from typing import Optional, List
from enum import StrEnum
import re
from src.core.constants import (
    ISBN_MIN_LENGTH, ISBN_MAX_LENGTH,
    DEFAULT_PAGE_SIZE, MAX_PAGE_SIZE
)


ISBN_PATTERN = re.compile(r'^(?:\d{9}[\dX]|\d{13})$')


class BookCondition(StrEnum):
    NEW = "new"
    GOOD = "good"
    FAIR = "fair"
    POOR = "poor"


class BookStatus(StrEnum):
    AVAILABLE = "available"
    RESERVED = "reserved"
    BORROWED = "borrowed"
    UNAVAILABLE = "unavailable"
    LENT = "lent"


def validate_isbn_format(v: str) -> str:
    cleaned = v.replace('-', '').replace(' ', '').upper()
    if not ISBN_PATTERN.match(cleaned):
        raise ValueError('Invalid ISBN format. Must be ISBN-10 (10 chars) or ISBN-13 (13 digits)')
    return cleaned


class BookBase(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    
    title: str = Field(..., min_length=1, max_length=500, description="Book title", examples=["Władca Pierścieni"]) 
    author: Optional[str] = Field(None, min_length=1, max_length=200, description="Book author", examples=["J.R.R. Tolkien"])
    isbn: str = Field(..., description="ISBN-10 or ISBN-13", examples=["9780261102385", "978-83-123-4567-8"])
    description: Optional[str] = Field(None, max_length=2000, description="Book description", examples=["Epicka powieść fantasy..."])
    publisher: Optional[str] = Field(None, max_length=200, description="Book publisher", examples=["Wydawnictwo XYZ"])
    publication_year: Optional[int] = Field(None, ge=1000, le=2100, description="Year of publication", examples=[1954])
    page_count: Optional[int] = Field(None, ge=1, description="Number of pages", examples=[423])
    language: Optional[str] = Field(None, max_length=50, description="Book language", examples=["pl", "en"])
    genre: Optional[str] = Field(None, max_length=100, description="Book genre", examples=["Fantasy"])
    
    @field_validator('isbn')
    @classmethod
    def validate_isbn(cls, v: str) -> str:
        return validate_isbn_format(v)


class BookCreate(BookBase):
    cover_url: Optional[str] = Field(None, max_length=500, description="Path or URL to book cover image", examples=["/covers/9780261102385.jpg"])


class BookUpdate(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    
    title: Optional[str] = Field(None, min_length=1, max_length=500, description="Book title")  
    author: Optional[str] = Field(None, min_length=1, max_length=200, description="Book author")
    description: Optional[str] = Field(None, max_length=2000, description="Book description")
    publisher: Optional[str] = Field(None, max_length=200, description="Book publisher")
    publication_year: Optional[int] = Field(None, ge=1000, le=2100, description="Year of publication")
    page_count: Optional[int] = Field(None, ge=1, description="Number of pages")
    language: Optional[str] = Field(None, max_length=50, description="Book language")
    genre: Optional[str] = Field(None, max_length=100, description="Book genre")
    cover_url: Optional[str] = Field(None, max_length=500, description="Path or URL to book cover")


class UpdateLendableRequest(BaseModel):
    is_lendable: bool = Field(..., description="Whether this book can be lent to others")


class UpdateStatusRequest(BaseModel):
    status: BookStatus = Field(..., description="Book status")


class OwnerInfo(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    location: Optional[str] = None


class BookResponse(BookBase):
    model_config = ConfigDict(populate_by_name=True, from_attributes=True)
    
    id: UUID
    cover_url: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class UserBookResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True, from_attributes=True)
    
    id: UUID
    status: BookStatus = Field(..., description="Book status")
    condition: Optional[BookCondition] = Field(None, description="Book condition")
    is_lendable: bool = Field(default=True, description="Whether this copy can be lent")
    book: BookResponse
    added_at: datetime
    updated_at: datetime


class CommunityBookResponse(BookBase):
    model_config = ConfigDict(populate_by_name=True, from_attributes=True)
    
    id: UUID
    user_book_id: UUID = Field(..., description="ID of the user's book copy for loan requests")
    isbn: Optional[str] = None
    cover_url: Optional[str] = None
    publisher: Optional[str] = None
    publication_year: Optional[int] = None
    page_count: Optional[int] = None
    owner_id: UUID
    owner: OwnerInfo
    status: BookStatus
    condition: Optional[BookCondition] = None
    is_lendable: bool
    created_at: datetime
    updated_at: datetime


class AddBookToLibraryRequest(BaseModel):   
    model_config = ConfigDict(populate_by_name=True)
    
    isbn: str = Field(..., min_length=ISBN_MIN_LENGTH, max_length=ISBN_MAX_LENGTH, description="ISBN-10 or ISBN-13")
    condition: BookCondition = Field(default=BookCondition.GOOD, description="Book condition")
    
    @field_validator('isbn')
    @classmethod
    def validate_isbn(cls, v: str) -> str:
        return validate_isbn_format(v)


class CommunityBooksFilter(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    
    status: Optional[str] = Field(None, description="Filter by status")
    search: Optional[str] = Field(None, description="Search in title, author")
    author: Optional[str] = Field(None, description="Filter by author")
    page: int = Field(1, ge=1, description="Page number")
    per_page: int = Field(DEFAULT_PAGE_SIZE, ge=1, le=MAX_PAGE_SIZE, description="Items per page")
    
    @field_validator('status')
    @classmethod
    def validate_status(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        valid_statuses = [s.value for s in BookStatus] + ['all']
        if v not in valid_statuses:
            raise ValueError(f"Invalid status. Must be one of: {', '.join(valid_statuses)}")
        return v



