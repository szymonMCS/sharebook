from pydantic import BaseModel, Field, ConfigDict, field_validator
from datetime import datetime
from uuid import UUID
from typing import Optional, List
import re


ISBN_PATTERN = re.compile(r'^(?:\d{9}[\dX]|\d{13})$')


class BookBase(BaseModel):

    model_config = ConfigDict(populate_by_name=True)
    
    title: str = Field(..., min_length=1, max_length=500, description="Book title", examples=["Władca Pierścieni"]) 
    author: Optional[str] = Field(None, min_length=1, max_length=200, description="Book author", examples=["J.R.R. Tolkien"])
    isbn: Optional[str] = Field(None, description="ISBN-10 or ISBN-13", examples=["9780261102385", "978-83-123-4567-8"])
    description: Optional[str] = Field(None, max_length=2000, description="Book description", examples=["Epicka powieść fantasy..."])
    publisher: Optional[str] = Field(None, max_length=200, description="Book publisher", examples=["Wydawnictwo XYZ"])
    publication_year: Optional[int] = Field(None, ge=1000, le=2100, description="Year of publication", examples=[1954])
    page_count: Optional[int] = Field(None, ge=1, description="Number of pages", examples=[423])
    language: Optional[str] = Field(None, max_length=50, description="Book language", examples=["pl", "en"])
    genre: Optional[str] = Field(None, max_length=100, description="Book genre", examples=["Fantasy"])
    
    @field_validator('isbn')
    @classmethod
    def validate_isbn(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        cleaned = v.replace('-', '').replace(' ', '').upper()
        if not ISBN_PATTERN.match(cleaned):
            raise ValueError('Invalid ISBN format. Must be ISBN-10 (10 chars) or ISBN-13 (13 digits)')
        return cleaned


class BookCreate(BookBase):
    
    cover_path: Optional[str] = Field(None, max_length=500, description="Path or URL to book cover image", examples=["/covers/9780261102385.jpg"])


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
    cover_path: Optional[str] = Field(None, max_length=500, description="Path or URL to book cover")


class UpdateLendableRequest(BaseModel):
    
    is_lendable: bool = Field(..., description="Whether this book can be lent to others")


class UpdateStatusRequest(BaseModel):
    
    status: str = Field(..., description="Book status: available, reserved, borrowed, unavailable, lent")
    
    @field_validator('status')
    @classmethod
    def validate_status(cls, v: str) -> str:
        valid_statuses = ['available', 'reserved', 'borrowed', 'unavailable', 'lent']
        if v not in valid_statuses:
            raise ValueError(f'Invalid status. Must be one of: {', '.join(valid_statuses)}')
        return v


class OwnerInfo(BaseModel):

    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    location: Optional[str] = None


class BookResponse(BookBase):

    model_config = ConfigDict(populate_by_name=True, from_attributes=True)
    
    id: UUID
    cover_path: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class UserBookResponse(BaseModel):

    model_config = ConfigDict(populate_by_name=True, from_attributes=True)
    
    id: UUID
    status: str = Field(..., description="Status: available, reserved, borrowed, unavailable")
    condition: Optional[str] = Field(None, description="Condition: new, good, fair, poor")
    is_lendable: bool = Field(default=True, description="Whether this copy can be lent")
    book: BookResponse
    added_at: datetime
    updated_at: datetime


class BookWithOwnersResponse(BookResponse):

    owners: List[OwnerInfo] = Field(default_factory=list, description="List of users who own this book")
    available_count: int = Field(default=0, description="Number of available copies")


class CommunityBookResponse(BookBase):
    
    model_config = ConfigDict(populate_by_name=True, from_attributes=True)
    
    id: UUID
    cover_url: Optional[str] = None
    publisher: Optional[str] = None
    publication_year: Optional[int] = None
    page_count: Optional[int] = None
    owner_id: UUID
    owner: OwnerInfo
    status: str
    condition: Optional[str] = None
    is_lendable: bool
    created_at: datetime
    updated_at: datetime


class BookCondition:
    """Valid book conditions."""
    NEW = "new"
    GOOD = "good"
    FAIR = "fair"
    POOR = "poor"
    
    ALL = [NEW, GOOD, FAIR, POOR]


class AddBookToLibraryRequest(BaseModel):
    """Request to add book to user's library.
    
    Only ISBN and condition required. Multiple copies allowed.
    """
    
    model_config = ConfigDict(populate_by_name=True)
    
    isbn: str = Field(..., min_length=10, max_length=17, description="ISBN-10 or ISBN-13")
    condition: str = Field(..., description="Book condition: new, good, fair, poor")
    
    @field_validator('isbn')
    @classmethod
    def validate_isbn(cls, v: str) -> str:
        cleaned = v.replace('-', '').replace(' ', '').upper()
        if not ISBN_PATTERN.match(cleaned):
            raise ValueError('Invalid ISBN format. Must be ISBN-10 (10 chars) or ISBN-13 (13 digits)')
        return cleaned
    
    @field_validator('condition')
    @classmethod
    def validate_condition(cls, v: str) -> str:
        if v not in BookCondition.ALL:
            raise ValueError(f'Invalid condition. Must be one of: {', '.join(BookCondition.ALL)}')
        return v
