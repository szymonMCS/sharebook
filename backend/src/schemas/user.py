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
    password: str = Field(..., min_length=8, examples=["SecurePass123!"], description="Password must be at least 8 characters and strong enough")
    first_name: str = Field(..., min_length=1, max_length=100, examples=["Jan"], description="User first name")
    last_name: str = Field(...,  min_length=1, max_length=100, examples=["Kowalski"], description="User last name")
    location: str = Field(...,  max_length=200, examples=["Warszawa"], description="User location (city) for book exchanges")
    phone: Optional[str] = Field(None, max_length=50, examples=["+48 123 456 789"], description="Contact phone number")

    @field_validator('password')
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        result = zxcvbn(v)
        if result['score'] < 4:
            suggestions = result['feedback'].get('suggestions', [])
            suggestion_map = {
                'Add another word or two. Uncommon words are better.': 'Dodaj kolejne słowa. Mniej popularne słowa są lepsze.',
                'Use a few words, avoid common phrases.': 'Użyj kilku słów, unikaj popularnych fraz.',
                'No need for symbols, digits, or uppercase letters.': 'Nie potrzebujesz symboli, cyfr ani wielkich liter - długość jest ważniejsza.',
                'Avoid repeated words and characters.': 'Unikaj powtarzających się słów i znaków.',
                'Avoid sequences like abc or 6543.': 'Unikaj sekwencji jak abc czy 1234.',
                'Avoid recent years.': 'Unikaj ostatnich lat.',
                'Avoid years that are associated with you.': 'Unikaj lat związanych z Tobą (rok urodzenia).',
                'Avoid dates and years that are associated with you.': 'Unikaj dat i lat związanych z Tobą.',
                'Capitalization doesn\'t help very much.': 'Wielkie litery niewiele pomagają.',
                'All-uppercase is almost as easy to guess as all-lowercase.': 'Same wielkie litery są prawie tak łatwe do odgadnięcia jak same małe.',
                'Reversed words aren\'t much harder to guess.': 'Odwrócone słowa nie są dużo trudniejsze do odgadnięcia.',
                'Predictable substitutions like \'@\' instead of \'a\' don\'t help very much.': 'Przewidywalne zamiany jak "@" zamiast "a" niewiele pomagają.',
            }
            translated = [suggestion_map.get(s, s) for s in suggestions]
            if translated:
                msg = f"Hasło jest za słabe. {' '.join(translated)}"
            else:
                msg = "Hasło jest za słabe. Użyj dłuższego hasła (min. 12-14 znaków) z różnymi słowami."
            raise ValueError(msg)
        return v


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



