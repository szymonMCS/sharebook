"""
Admin Service - operacje administracyjne zgodne z SOLID.

SRP: TYLKO operacje admina - nie autentykacja, nie wypożyczenia!
DIP: Zależy od interfejsów repozytoriów (IUserRepository, IBookRepository).
"""

import logging
import secrets
from uuid import UUID
from typing import Optional
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import User, Book, Loan, UserBook
from database.interfaces import IUserRepository, IBookRepository
from src.core.security import get_password_hash
from src.core.exceptions import UserNotFoundException, BookNotFoundException
from src.services.interfaces import IAdminService
from fastapi import HTTPException

logger = logging.getLogger(__name__)


class AdminService(IAdminService):
    """
    Serwis dla operacji administracyjnych.
    
    SRP: TYLKO operacje admina - nie autentykacja, nie wypożyczenia!
    
    DIP: Zależy od interfejsów repozytoriów:
    - IUserRepository (zamiast UserRepository)
    - IBookRepository (zamiast BookRepository)
    
    ZAKRES:
    - Dashboard (statystyki)
    - Zarządzanie użytkownikami (CRUD, role)
    - Moderacja książek
    """
    
    def __init__(
        self,
        db: AsyncSession,
        user_repo: Optional[IUserRepository] = None,
        book_repo: Optional[IBookRepository] = None
    ):
        """
        Inicjalizacja serwisu admina.
        
        Args:
            db: Sesja bazy danych
            user_repo: Repozytorium użytkowników (interfejs - DIP)
            book_repo: Repozytorium książek (interfejs - DIP)
        """
        self._db = db
        
        # DIP: Używamy interfejsów, nie konkretów
        if user_repo:
            self._user_repo = user_repo
        else:
            from database.repositories.user_repository import UserRepository
            self._user_repo = UserRepository(db)
        
        if book_repo:
            self._book_repo = book_repo
        else:
            from database.repositories.book_repository import BookRepository
            self._book_repo = BookRepository(db)
    
    # ═════════════════════════════════════════════════════════════════
    # STATYSTYKI DASHBOARDU
    # ═════════════════════════════════════════════════════════════════
    
    async def get_dashboard_stats(self) -> dict:
        """
        Pobiera statystyki systemu dla dashboardu admina.
        
        Returns:
            dict: Statystyki (użytkownicy, książki, wypożyczenia)
        """
        # Użytkownicy
        total_users = await self._db.scalar(
            select(func.count()).select_from(User)
        )
        
        # Książki
        total_books = await self._db.scalar(
            select(func.count()).select_from(Book)
        )
        
        # Wypożyczenia
        total_loans = await self._db.scalar(
            select(func.count()).select_from(Loan)
        )
        
        # Aktywne prośby (reserved)
        pending_requests = await self._db.scalar(
            select(func.count())
            .select_from(UserBook)
            .where(UserBook.status == "reserved")
        )
        
        return {
            "total_users": total_users or 0,
            "total_books": total_books or 0,
            "total_loans": total_loans or 0,
            "pending_requests": pending_requests or 0
        }
    
    # ═════════════════════════════════════════════════════════════════
    # ZARZĄDZANIE UŻYTKOWNIKAMI
    # ═════════════════════════════════════════════════════════════════
    
    async def list_users(
        self,
        page: int = 1,
        per_page: int = 20,
        search: Optional[str] = None
    ) -> dict:
        """
        Lista użytkowników z paginacją.
        
        Args:
            page: Numer strony (1-indexed)
            per_page: Ilość na stronę
            search: Opcjonalne wyszukiwanie
            
        Returns:
            dict: Lista użytkowników + metadane paginacji
        """
        skip = (page - 1) * per_page
        
        # DIP: Używamy interfejsu repozytorium
        users, total = await self._user_repo.get_multi(
            skip=skip,
            limit=per_page
        )
        
        return {
            "data": [
                {
                    "id": str(u.id),
                    "email": u.email,
                    "first_name": u.first_name,
                    "last_name": u.last_name,
                    "role": u.role,
                    "is_active": u.is_active,
                    "created_at": u.created_at.isoformat() if u.created_at else None
                }
                for u in users
            ],
            "total": total,
            "page": page,
            "per_page": per_page,
            "total_pages": (total + per_page - 1) // per_page if per_page > 0 else 0
        }
    
    async def update_user_role(
        self,
        user_id: UUID,
        new_role: str,
        current_admin_id: UUID
    ) -> dict:
        """
        Zmienia rolę użytkownika.
        
        WALIDACJA:
        - Tylko "reader" lub "admin"
        - Nie można zmienić własnej roli (ochrona przed degradacją)
        
        Args:
            user_id: ID użytkownika
            new_role: Nowa rola ("reader" lub "admin")
            current_admin_id: ID admina wykonującego operację
            
        Returns:
            dict: Zaktualizowany użytkownik
        """
        # Nie można zmienić własnej roli
        if user_id == current_admin_id:
            raise HTTPException(
                status_code=400,
                detail="Nie możesz zmienić własnej roli"
            )
        
        # Walidacja roli
        if new_role not in ["reader", "admin"]:
            raise HTTPException(
                status_code=400,
                detail="Nieprawidłowa rola. Użyj 'reader' lub 'admin'"
            )
        
        # Pobierz użytkownika przez interfejs (DIP)
        user = await self._user_repo.get(user_id)
        if not user:
            raise UserNotFoundException(str(user_id))
        
        # Aktualizuj rolę
        user.role = new_role
        await self._user_repo.update(user)
        
        logger.info(f"Admin {current_admin_id} changed role of user {user_id} to {new_role}")
        
        return {
            "id": str(user.id),
            "email": user.email,
            "role": user.role
        }
    
    async def reset_user_password(
        self,
        user_id: UUID,
        current_admin_id: UUID
    ) -> dict:
        """
        Resetuje hasło użytkownika do tymczasowego.
        
        Args:
            user_id: ID użytkownika
            current_admin_id: ID admina wykonującego operację
            
        Returns:
            dict: Tymczasowe hasło (pokazane tylko raz!)
        """
        # Nie można zresetować własnego hasła tą metodą
        if user_id == current_admin_id:
            raise HTTPException(
                status_code=400,
                detail="Użyj endpointu zmiany hasła do zmiany własnego hasła"
            )
        
        # Pobierz użytkownika przez interfejs (DIP)
        user = await self._user_repo.get(user_id)
        if not user:
            raise UserNotFoundException(str(user_id))
        
        # Generuj tymczasowe hasło
        temp_password = secrets.token_urlsafe(12)
        
        # Hashuj i zapisz
        user.hashed_password = get_password_hash(temp_password)
        await self._user_repo.update(user)
        
        logger.info(f"Admin {current_admin_id} reset password for user {user_id}")
        
        return {
            "message": "Hasło zresetowane",
            "temp_password": temp_password  # Pokaż tylko raz!
        }
    
    async def delete_user(
        self,
        user_id: UUID,
        current_admin_id: UUID
    ) -> None:
        """
        Usuwa użytkownika (HARD DELETE).
        
        BEZPIECZEŃSTWO:
        - Nie można usunąć samego siebie
        - Kaskadowe usuwanie relacji (SQLAlchemy cascade)
        
        Args:
            user_id: ID użytkownika do usunięcia
            current_admin_id: ID admina wykonującego operację
        """
        # Nie można usunąć samego siebie
        if user_id == current_admin_id:
            raise HTTPException(
                status_code=400,
                detail="Nie możesz usunąć własnego konta"
            )
        
        # Pobierz użytkownika przez interfejs (DIP)
        user = await self._user_repo.get(user_id)
        if not user:
            raise UserNotFoundException(str(user_id))
        
        # Usuń przez interfejs (DIP)
        await self._user_repo.delete(user_id)
        
        logger.info(f"Admin {current_admin_id} deleted user {user_id}")
    
    # ═════════════════════════════════════════════════════════════════
    # MODERACJA KSIĄŻEK
    # ═════════════════════════════════════════════════════════════════
    
    async def list_books(
        self,
        page: int = 1,
        per_page: int = 20
    ) -> dict:
        """
        Lista wszystkich książek (admin view).
        
        Args:
            page: Numer strony
            per_page: Ilość na stronę
            
        Returns:
            dict: Lista książek + paginacja
        """
        skip = (page - 1) * per_page
        
        # DIP: Używamy interfejsu
        books, total = await self._book_repo.get_multi(
            skip=skip,
            limit=per_page
        )
        
        return {
            "data": [
                {
                    "id": str(b.id),
                    "title": b.title,
                    "author": b.author,
                    "isbn": b.isbn,
                    "created_at": b.created_at.isoformat() if b.created_at else None
                }
                for b in books
            ],
            "total": total,
            "page": page,
            "per_page": per_page,
            "total_pages": (total + per_page - 1) // per_page if per_page > 0 else 0
        }
    
    async def delete_book(self, book_id: UUID) -> None:
        """
        Usuwa książkę (moderacja).
        
        Args:
            book_id: ID książki do usunięcia
        """
        # Pobierz książkę przez interfejs (DIP)
        book = await self._book_repo.get(book_id)
        if not book:
            raise BookNotFoundException(str(book_id))
        
        # TODO: Sprawdź czy książka nie jest aktualnie wypożyczona
        
        # Usuń przez interfejs (DIP)
        await self._book_repo.delete(book_id)
        
        logger.info(f"Admin deleted book {book_id}")
