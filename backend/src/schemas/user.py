from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict, EmailStr, field_validator
from uuid import UUID
from typing import Optional
from zxcvbn import zxcvbn


class UserBase(BaseModel):

    model_config = ConfigDict(populate_by_name=True)
    
    email: EmailStr = Field(..., examples=["user@example.com"])
    role: str = Field(default="reader", examples=["reader", "admin"], description="User role: 'reader' or 'admin'")


class UserCreate(UserBase):
    
    password: str = Field(..., min_length=8, examples=["SecurePass123!"], description="Password must be at least 8 characters") 
    first_name: str = Field(..., min_length=1, max_length=100, examples=["Jan"], description="User first name")
    last_name: str = Field(...,  min_length=1, max_length=100, examples=["Kowalski"], description="User last name")
    location: str = Field(...,  max_length=200, examples=["Warszawa"], description="User location (city) for book exchanges")
    phone: str = Field(..., max_length=50, examples=["+48 123 456 789"], description="Contact phone number")

    @field_validator('password')
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        result = zxcvbn(v)
        if result['score'] < 2:  # 0-4 scale
            raise ValueError(f'Password too weak: {result["feedback"]["warning"] or "Use stronger password"}')
        return v


class UserCreateInternal(UserBase):

    model_config = ConfigDict(populate_by_name=True)
    
    hashed_password: str
    first_name: str
    last_name: str
    location: str
    phone: Optional[str] = None


class UserUpdate(BaseModel):

    model_config = ConfigDict(populate_by_name=True)
    
    first_name: Optional[str] = Field(None, min_length=1, max_length=100, examples=["Jan"])
    last_name: Optional[str] = Field(None, min_length=1, max_length=100, examples=["Kowalski"])
    bio: Optional[str] = Field(None, max_length=1000, description="User bio or description", examples=["Miłośnik literatury fantasy i science fiction."])
    location: Optional[str] = Field(None, max_length=200, description="User location (city, region)", examples=["Warszawa, Polska"])
    phone: Optional[str] = Field(None, max_length=50, description="Contact phone number", examples=["+48 123 456 789"])


class UserResponse(UserBase):

    model_config = ConfigDict(populate_by_name=True, from_attributes=True)

    id: UUID  
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    location: Optional[str] = None
    is_active: bool
    created_at: datetime


class UserProfileResponse(UserResponse):

    model_config = ConfigDict(populate_by_name=True, from_attributes=True)
    
    bio: Optional[str] = Field(None, max_length=1000)
    phone: Optional[str] = Field(None, max_length=50)
    avatar_url: Optional[str] = Field(None, max_length=500, description="URL to user avatar image", examples=["https://example.com/avatar.jpg"])
    books_count: int = Field(default=0, description="Number of books owned by the user", examples=[5])


class TokenResponse(BaseModel):

    model_config = ConfigDict(populate_by_name=True)
    
    access_token: str  
    refresh_token: str  
    token_type: str = "bearer"  
