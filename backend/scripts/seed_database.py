import asyncio
import json
import sys
from pathlib import Path
from uuid import uuid4
from datetime import datetime

# Fix Windows console encoding
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

# Load environment variables before importing config
from dotenv import load_dotenv
env_path = backend_dir.parent / ".env"
load_dotenv(dotenv_path=str(env_path))

from sqlalchemy import select
from database.config import AsyncSessionLocal, init_db
from database.models import User, Book, UserBook
from src.core.security import get_password_hash

USERS_DATA = [
    {
        "email": "admin@sharebook.pl",
        "password": "admin123",
        "first_name": "Administrator",
        "last_name": "Systemu",
        "location": "Warszawa",
        "role": "admin",
        "is_superuser": True,
    },
    {
        "email": "anna.kowalska@example.com",
        "password": "test123",
        "first_name": "Anna",
        "last_name": "Kowalska",
        "location": "Warszawa",
        "role": "reader",
        "is_superuser": False,
    },
    {
        "email": "piotr.nowak@example.com",
        "password": "test123",
        "first_name": "Piotr",
        "last_name": "Nowak",
        "location": "Kraków",
        "role": "reader",
        "is_superuser": False,
    },
    {
        "email": "maria.wisniewska@example.com",
        "password": "test123",
        "first_name": "Maria",
        "last_name": "Wiśniewska",
        "location": "Wrocław",
        "role": "reader",
        "is_superuser": False,
    },
    {
        "email": "jan.wojcik@example.com",
        "password": "test123",
        "first_name": "Jan",
        "last_name": "Wójcik",
        "location": "Gdańsk",
        "role": "reader",
        "is_superuser": False,
    },
    {
        "email": "katarzyna.zielinska@example.com",
        "password": "test123",
        "first_name": "Katarzyna",
        "last_name": "Zielińska",
        "location": "Poznań",
        "role": "reader",
        "is_superuser": False,
    },
    {
        "email": "katarzyna.lewandowska@example.com",
        "password": "test123",
        "first_name": "Katarzyna",
        "last_name": "Lewandowska",
        "location": "Łódź",
        "role": "reader",
        "is_superuser": False,
    },
]


# Mapping condition values from JSON to database format
CONDITION_MAPPING = {
    "like_new": "new",
    "very_good": "good",
    "good": "good",
    "fair": "fair",
    "poor": "poor",
}


def load_books_from_json():
    """Load book data from books_data.json file."""
    json_path = Path(__file__).parent / "books_data.json"
    if not json_path.exists():
        print(f"  ⚠️  Plik {json_path} nie istnieje, pominięto")
        return []
    
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    return data.get("books", [])


async def seed_users(db):
    """Seed users from USERS_DATA."""
    print("Tworzenie użytkowników...")
    users_created = 0
    users_by_email = {}
    
    for user_data in USERS_DATA:
        result = await db.execute(
            select(User).where(User.email == user_data["email"])
        )
        existing = result.scalar_one_or_none()
        
        if existing:
            print(f"  • {user_data['email']} - już istnieje")
            users_by_email[existing.email] = existing
        else:
            user = User(
                id=uuid4(),
                email=user_data["email"],
                hashed_password=get_password_hash(user_data["password"]),
                first_name=user_data["first_name"],
                last_name=user_data["last_name"],
                location=user_data["location"],
                role=user_data["role"],
                is_active=True,
                is_superuser=user_data["is_superuser"],
            )
            db.add(user)
            users_created += 1
            print(f"  • {user_data['email']} - utworzony")
            users_by_email[user.email] = user
    
    await db.commit()
    print(f"[OK] Utworzono {users_created} nowych użytkowników\n")
    return users_by_email


async def seed_books_from_json(db, users_by_email):
    """Seed books and user_books from books_data.json."""
    books_data = load_books_from_json()
    if not books_data:
        print("Brak danych z JSON do importu\n")
        return 0, 0
    
    # Remove duplicates by ISBN (keep first occurrence)
    seen_isbns = set()
    unique_books = []
    for book_data in books_data:
        isbn = book_data.get("isbn")
        if isbn and isbn not in seen_isbns:
            seen_isbns.add(isbn)
            unique_books.append(book_data)
    
    duplicates = len(books_data) - len(unique_books)
    if duplicates:
        print(f"Znaleziono i pominięto {duplicates} duplikatów ISBN")
    
    print(f"Importowanie {len(unique_books)} unikalnych książek z pliku JSON...")
    
    books_created = 0
    user_books_created = 0
    books_by_isbn = {}
    
    # First pass: create all books
    for book_data in unique_books:
        isbn = book_data.get("isbn")
        if not isbn:
            continue
            
        result = await db.execute(
            select(Book).where(Book.isbn == isbn)
        )
        existing = result.scalar_one_or_none()
        
        if existing:
            books_by_isbn[isbn] = existing
        else:
            book = Book(
                id=uuid4(),
                isbn=isbn,
                title=book_data["title"],
                author=book_data.get("author"),
                description=book_data.get("description"),
                publisher=book_data.get("publisher"),
                publication_year=book_data.get("publication_year"),
                page_count=book_data.get("page_count"),
                language=book_data.get("language", "pl"),
                genre=book_data.get("genre"),
                cover_url=book_data.get("cover_url"),
            )
            db.add(book)
            books_by_isbn[isbn] = book
            books_created += 1
    
    await db.commit()
    print(f"  [OK] Utworzono {books_created} nowych książek w katalogu")
    
    # Refresh all book objects to get their IDs
    for book in books_by_isbn.values():
        await db.refresh(book)
    
    # Second pass: create user_books
    for book_data in unique_books:
        user_email = book_data.get("user_email")
        isbn = book_data.get("isbn")
        
        if not user_email or not isbn:
            continue
        
        user = users_by_email.get(user_email)
        book = books_by_isbn.get(isbn)
        
        if not user or not book:
            print(f"  ⚠️  Pominięto: brak użytkownika ({user_email}) lub książki ({isbn})")
            continue
        
        # Check if this user_book already exists
        result = await db.execute(
            select(UserBook).where(
                UserBook.user_id == user.id,
                UserBook.book_id == book.id
            )
        )
        if result.scalar_one_or_none():
            continue
        
        # Map condition value
        raw_condition = book_data.get("condition", "good")
        condition = CONDITION_MAPPING.get(raw_condition, raw_condition)
        
        user_book = UserBook(
            id=uuid4(),
            user_id=user.id,
            book_id=book.id,
            status=book_data.get("status", "available"),
            condition=condition,
            is_lendable=book_data.get("is_lendable", True),
        )
        db.add(user_book)
        user_books_created += 1
        print(f"  • {user.first_name} - {book.title[:30]}... ({condition})")
    
    await db.commit()
    print(f"[OK] Utworzono {user_books_created} egzemplarzy użytkowników z JSON\n")
    return books_created, user_books_created


async def seed_database():
    print("=" * 60)
    print("ShareBook - Database Seeder")
    print("=" * 60)
    
    await init_db()
    print("[OK] Baza danych zainicjalizowana\n")
    
    async with AsyncSessionLocal() as db:
        # Seed users first
        users_by_email = await seed_users(db)
        
        # Seed books and user_books from JSON
        await seed_books_from_json(db, users_by_email)
        
        # Print summary
        print("=" * 60)
        print("PODSUMOWANIE")
        print("=" * 60)
        
        result = await db.execute(select(User))
        total_users = len(result.scalars().all())
        
        result = await db.execute(select(Book))
        total_books = len(result.scalars().all())
        
        result = await db.execute(select(UserBook))
        total_user_books = len(result.scalars().all())
        
        result = await db.execute(
            select(UserBook).where(UserBook.status == "available")
        )
        available_books = len(result.scalars().all())
        
        print(f"Użytkownicy:     {total_users}")
        print(f"Książki:         {total_books}")
        print(f"Egzemplarze:     {total_user_books}")
        print(f"Dostępne:        {available_books}")
        print()
        print("Dane logowania:")
        print("-" * 60)
        for user_data in USERS_DATA:
            role_label = "(admin)" if user_data["is_superuser"] else "(user)"
            print(f"  {user_data['email']:<35} / {user_data['password']:<10} {role_label}")
        print("=" * 60)
        print("[OK] Seedowanie zakończone sukcesem!")


if __name__ == "__main__":
    asyncio.run(seed_database())
