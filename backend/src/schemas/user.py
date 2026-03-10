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


class UserCreateInternal(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    
    email: EmailStr
    hashed_password: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    location: Optional[str] = None
    phone: Optional[str] = None
    role: str = "reader"
    is_active: bool = True

    @field_validator('password', check_fields=False)
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        result = zxcvbn(v)
        if result['score'] < 2:  # 0-4 scale
            raise ValueError(f'Password too weak: {result["feedback"]["warning"] or "Use stronger password"}')
        return v


class UserUpdate(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    
    first_name: Optional[str] = Field(None, min_length=1, max_length=100, examples=["Jan"])
    last_name: Optional[str] = Field(None, min_length=1, max_length=100, examples=["Kowalski"])
    location: Optional[str] = Field(None, max_length=200, description="User location (city, region)", examples=["Warszawa, Polska"])
    phone: Optional[str] = Field(None, max_length=50, description="Contact phone number", examples=["+48 123 456 789"])


class UserResponse(UserBase):
    model_config = ConfigDict(populate_by_name=True, from_attributes=True)

    id: UUID  
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    location: Optional[str] = None
    phone: Optional[str] = None
    bio: Optional[str] = None
    avatar_url: Optional[str] = None
    is_active: bool
    is_superuser: bool = False
    created_at: datetime
    updated_at: datetime


class UserProfileResponse(UserResponse):
    model_config = ConfigDict(populate_by_name=True, from_attributes=True)
    
    bio: Optional[str] = None
    avatar_url: Optional[str] = None
    books_count: int = Field(default=0, description="Number of books owned by the user", examples=[5])


class TokenResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    
    access_token: str  
    refresh_token: str  
    token_type: str = "bearer"  
