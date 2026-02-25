import asyncio
import sys
from pathlib import Path
from uuid import uuid4
from datetime import datetime

backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

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
]

BOOKS_DATA = [
    {
        "isbn": "9788382027617",
        "title": "Władca Pierścieni",
        "author": "J.R.R. Tolkien",
        "description": "Epicka powieść fantasy, która przenosi czytelnika do świata Śródziemia.",
        "publisher": "Muza",
        "publication_year": 1954,
        "page_count": 586,
        "language": "pl",
        "genre": "Fantasy",
        "cover_path": "https://covers.openlibrary.org/b/isbn/9788382027617-M.jpg",
    },
    {
        "isbn": "9788382656824",
        "title": "Harry Potter i Kamień Filozoficzny",
        "author": "J.K. Rowling",
        "description": "Pierwszy tom serii o młodym czarodzieju Harrym Potterze.",
        "publisher": "Media Rodzina",
        "publication_year": 1997,
        "page_count": 320,
        "language": "pl",
        "genre": "Fantasy",
        "cover_path": "https://covers.openlibrary.org/b/isbn/9788382656824-M.jpg",
    },
    {
        "isbn": "9788376489650",
        "title": "Duma i uprzedzenie",
        "author": "Jane Austen",
        "description": "Klasyczna powieść obyczajowa o miłości i konwencjach społecznych.",
        "publisher": "PWN",
        "publication_year": 1813,
        "page_count": 279,
        "language": "pl",
        "genre": "Powieść obyczajowa",
        "cover_path": "https://covers.openlibrary.org/b/isbn/9788376489650-M.jpg",
    },
    {
        "isbn": "9788308058015",
        "title": "1984",
        "author": "George Orwell",
        "description": "Klasyczna dystopijna powieść o totalitarnym świecie.",
        "publisher": "Muza",
        "publication_year": 1949,
        "page_count": 328,
        "language": "pl",
        "genre": "Dystopia",
        "cover_path": "https://covers.openlibrary.org/b/isbn/9788308058015-M.jpg",
    },
    {
        "isbn": "9788320717509",
        "title": "Zbrodnia i kara",
        "author": "Fiodor Dostojewski",
        "description": "Psychologiczna powieść o młodym studencie i jego przestępstwie.",
        "publisher": "Znak",
        "publication_year": 1866,
        "page_count": 560,
        "language": "pl",
        "genre": "Literatura klasyczna",
        "cover_path": "https://covers.openlibrary.org/b/isbn/9788320717509-M.jpg",
    },
    {
        "isbn": "9788373012904",
        "title": "Mały Książę",
        "author": "Antoine de Saint-Exupéry",
        "description": "Filozoficzna bajka dla dzieci i dorosłych.",
        "publisher": "Nasza Księgarnia",
        "publication_year": 1943,
        "page_count": 96,
        "language": "pl",
        "genre": "Literatura dziecięca",
        "cover_path": "https://covers.openlibrary.org/b/isbn/9788373012904-M.jpg",
    },
    {
        "isbn": "9788366433152",
        "title": "Gra o Tron",
        "author": "George R.R. Martin",
        "description": "Pierwszy tom epickiej serii Pieśń Lodu i Ognia.",
        "publisher": "Zysk i S-ka",
        "publication_year": 1996,
        "page_count": 835,
        "language": "pl",
        "genre": "Fantasy",
        "cover_path": "https://covers.openlibrary.org/b/isbn/9788366433152-M.jpg",
    },
    {
        "isbn": "9788306038743",
        "title": "Hobbit",
        "author": "J.R.R. Tolkien",
        "description": "Przygody Bilba Bagginsa i jego towarzyszy.",
        "publisher": "Muza",
        "publication_year": 1937,
        "page_count": 320,
        "language": "pl",
        "genre": "Fantasy",
        "cover_path": "https://covers.openlibrary.org/b/isbn/9788306038743-M.jpg",
    },
    {
        "isbn": "9788378876088",
        "title": "Lalka",
        "author": "Bolesław Prus",
        "description": "Powieść społeczno-obyczajowa o miłości i pieniądzach.",
        "publisher": "Greg",
        "publication_year": 1890,
        "page_count": 640,
        "language": "pl",
        "genre": "Literatura polska",
        "cover_path": "https://covers.openlibrary.org/b/isbn/9788378876088-M.jpg",
    },
    {
        "isbn": "9788373272663",
        "title": "Pan Tadeusz",
        "author": "Adam Mickiewicz",
        "description": "Narodowa epopeja polska.",
        "publisher": "PWN",
        "publication_year": 1834,
        "page_count": 320,
        "language": "pl",
        "genre": "Poezja epicka",
        "cover_path": "https://covers.openlibrary.org/b/isbn/9788373272663-M.jpg",
    },
]

USER_BOOKS_MAPPING = {
    1: [0, 1, 2],     
    2: [3, 4],        
    3: [5, 6],        
    4: [7, 8, 9],      
}

async def seed_database():
    print("=" * 60)
    print("ShareBook - Database Seeder")
    print("=" * 60)
    
    await init_db()
    print("[OK] Baza danych zainicjalizowana")
    print()
    
    async with AsyncSessionLocal() as db:

        print("Tworzenie użytkowników...")
        users_created = 0
        users = []
        
        for user_data in USERS_DATA:
            result = await db.execute(
                select(User).where(User.email == user_data["email"])
            )
            existing = result.scalar_one_or_none()
            
            if existing:
                print(f"  • {user_data['email']} - już istnieje")
                users.append(existing)
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
                users.append(user)
                users_created += 1
                print(f"  • {user_data['email']} - utworzony")
        
        await db.commit()
        print(f"[OK] Utworzono {users_created} nowych użytkowników")
        print()
        
        print("Tworzenie książek w katalogu globalnym...")
        books_created = 0
        books = []
        
        for book_data in BOOKS_DATA:
            result = await db.execute(
                select(Book).where(Book.isbn == book_data["isbn"])
            )
            existing = result.scalar_one_or_none()
            
            if existing:
                print(f"  • {book_data['title'][:40]}... - już istnieje")
                books.append(existing)
            else:
                book = Book(
                    id=uuid4(),
                    **book_data
                )
                db.add(book)
                books.append(book)
                books_created += 1
                print(f"  • {book_data['title'][:40]}... - utworzona")
        
        await db.commit()
        print(f"[OK] Utworzono {books_created} nowych książek")
        print()
        
        for book in books:
            await db.refresh(book)
        for user in users:
            await db.refresh(user)
        

        print("Tworzenie egzemplarzy użytkowników...")
        user_books_created = 0
        
        for user_idx, book_indices in USER_BOOKS_MAPPING.items():
            user = users[user_idx]
            
            for book_idx in book_indices:
                book = books[book_idx]
                
                result = await db.execute(
                    select(UserBook).where(
                        UserBook.user_id == user.id,
                        UserBook.book_id == book.id
                    )
                )
                existing = result.scalar_one_or_none()
                
                if existing:
                    continue
                
                status = "available" if book_idx % 2 == 0 else "borrowed"
                
                user_book = UserBook(
                    id=uuid4(),
                    user_id=user.id,
                    book_id=book.id,
                    status=status,
                    condition="good",
                    is_lendable=True,
                )
                db.add(user_book)
                user_books_created += 1
                print(f"  • {user.first_name} - {book.title[:30]}... ({status})")
        
        await db.commit()
        print(f"[OK] Utworzono {user_books_created} egzemplarzy")
        print()
        
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
