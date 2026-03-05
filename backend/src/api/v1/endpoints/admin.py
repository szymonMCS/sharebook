"""Admin endpoints for user and system management."""
import logging
from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.deps import get_current_active_user, get_db
from src.services.admin_service import AdminService
from database.models import User

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/admin", tags=["admin"])


# ═══════════════════════════════════════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════════════════════════════════════

def check_admin(user: User) -> None:
    """
    Sprawdza czy użytkownik ma rolę administratora.
    
    DLACZEGO OSOBNA FUNKCJA?
    - DRY: Jedna funkcja współdzielona zamiast powtarzania w każdym endpoincie
    - Centralna kontrola: Zmiana logiki w jednym miejscu
    - Czytelność: `check_admin(current_user)` vs 4 linie if/raise
    
    Raises:
        HTTPException(403): Gdy użytkownik nie jest adminem
    """
    if user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Brak uprawnień administratora"
        )


# ═══════════════════════════════════════════════════════════════════════════
# DEPS - Fabryki z Dependency Injection (DIP)
# ═══════════════════════════════════════════════════════════════════════════

def get_admin_service(db: AsyncSession = Depends(get_db)) -> AdminService:
    """
    Fabryka dla AdminService z wstrzykniętymi zależnościami.
    
    DIP: Wstrzykujemy konkretne repozytoria, ale AdminService
         zależy od interfejsów (IUserRepository, IBookRepository).
    """
    return AdminService(db=db)


# ═══════════════════════════════════════════════════════════════════════════
# ENDPOINTY
# ═══════════════════════════════════════════════════════════════════════════

@router.get("/dashboard", response_model=dict)
async def get_dashboard(
    current_user: User = Depends(get_current_active_user),
    admin_service: AdminService = Depends(get_admin_service)
):
    """
    Dashboard admina ze statystykami systemu.
    
    Returns:
        Statystyki: total_users, total_books, total_loans, pending_requests
    """
    check_admin(current_user)
    
    stats = await admin_service.get_dashboard_stats()
    
    return {
        "success": True,
        "data": stats,
        "message": "Dashboard stats retrieved"
    }


@router.get("/users", response_model=dict)
async def get_users(
    page: int = Query(1, ge=1, description="Numer strony"),
    per_page: int = Query(20, ge=1, le=100, description="Ilość na stronę"),
    search: str = Query(None, description="Wyszukiwanie (opcjonalne)"),
    current_user: User = Depends(get_current_active_user),
    admin_service: AdminService = Depends(get_admin_service)
):
    """
    Lista użytkowników (admin only).
    
    Zwraca paginowaną listę wszystkich użytkowników w systemie.
    """
    check_admin(current_user)
    
    result = await admin_service.list_users(
        page=page,
        per_page=per_page,
        search=search
    )
    
    return {
        "success": True,
        "data": result,
        "message": "Users retrieved"
    }


@router.patch("/users/{user_id}/role", response_model=dict)
async def update_role(
    user_id: UUID,
    role_data: dict,
    current_user: User = Depends(get_current_active_user),
    admin_service: AdminService = Depends(get_admin_service)
):
    """
    Zmienia rolę użytkownika.
    
    Args:
        user_id: ID użytkownika
        role_data: {"role": "reader" | "admin"}
    
    Ochrona:
    - Nie można zmienić własnej roli
    - Dozwolone role: "reader", "admin"
    """
    check_admin(current_user)
    
    result = await admin_service.update_user_role(
        user_id=user_id,
        new_role=role_data.get("role"),
        current_admin_id=current_user.id
    )
    
    return {
        "success": True,
        "data": result,
        "message": f"Rola zmieniona na: {result['role']}"
    }


@router.post("/users/{user_id}/reset-password", response_model=dict)
async def reset_password(
    user_id: UUID,
    current_user: User = Depends(get_current_active_user),
    admin_service: AdminService = Depends(get_admin_service)
):
    """
    Resetuje hasło użytkownika do tymczasowego.
    
    Returns:
        Tymczasowe hasło (pokazane tylko raz!)
    
    Ochrona:
    - Nie można zresetować własnego hasła tą metodą
    """
    check_admin(current_user)
    
    result = await admin_service.reset_user_password(
        user_id=user_id,
        current_admin_id=current_user.id
    )
    
    return {
        "success": True,
        "data": result,
        "message": "Hasło zresetowane. Użytkownik powinien je zmienić przy pierwszym logowaniu."
    }


@router.delete("/users/{user_id}", response_model=dict)
async def delete_user(
    user_id: UUID,
    current_user: User = Depends(get_current_active_user),
    admin_service: AdminService = Depends(get_admin_service)
):
    """
    Usuwa użytkownika (HARD DELETE).
    
    Ochrona:
    - Nie można usunąć własnego konta
    - Kaskadowe usuwanie relacji (SQLAlchemy cascade)
    """
    check_admin(current_user)
    
    await admin_service.delete_user(
        user_id=user_id,
        current_admin_id=current_user.id
    )
    
    return {
        "success": True,
        "message": "Użytkownik usunięty"
    }


@router.get("/books", response_model=dict)
async def get_books(
    page: int = Query(1, ge=1, description="Numer strony"),
    per_page: int = Query(20, ge=1, le=100, description="Ilość na stronę"),
    current_user: User = Depends(get_current_active_user),
    admin_service: AdminService = Depends(get_admin_service)
):
    """
    Lista wszystkich książek (admin view).
    
    Zwraca paginowaną listę wszystkich książek w katalogu.
    """
    check_admin(current_user)
    
    result = await admin_service.list_books(
        page=page,
        per_page=per_page
    )
    
    return {
        "success": True,
        "data": result,
        "message": "Books retrieved"
    }


@router.delete("/books/{book_id}", response_model=dict)
async def delete_book(
    book_id: UUID,
    current_user: User = Depends(get_current_active_user),
    admin_service: AdminService = Depends(get_admin_service)
):
    """
    Usuwa książkę (moderacja).
    
    TODO: Sprawdź czy książka nie jest aktualnie wypożyczona
    """
    check_admin(current_user)
    
    await admin_service.delete_book(book_id)
    
    return {
        "success": True,
        "message": "Książka usunięta"
    }
