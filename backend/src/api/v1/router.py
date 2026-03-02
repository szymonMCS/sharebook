from fastapi import APIRouter
from src.api.v1.endpoints import auth, health, users, books, library, loan_requests, loans

api_router = APIRouter()

api_router.include_router(auth.router)
api_router.include_router(health.router)
api_router.include_router(users.router)

api_router.include_router(books.router)
api_router.include_router(library.router)
api_router.include_router(loan_requests.router)
api_router.include_router(loans.router)
