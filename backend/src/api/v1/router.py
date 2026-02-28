from fastapi import APIRouter
from src.api.v1.endpoints import auth, health, users, books, library

api_router = APIRouter()

api_router.include_router(auth.router)
api_router.include_router(health.router)
api_router.include_router(users.router)

api_router.include_router(books.router)
api_router.include_router(library.router)
