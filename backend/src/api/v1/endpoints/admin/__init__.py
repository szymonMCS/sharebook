from fastapi import APIRouter
from src.api.v1.endpoints.admin import dashboard, users, books

router = APIRouter()

router.include_router(dashboard.router, prefix="/dashboard", tags=["admin"])
router.include_router(users.router, prefix="/users", tags=["admin"])
router.include_router(books.router, prefix="/books", tags=["admin"])
