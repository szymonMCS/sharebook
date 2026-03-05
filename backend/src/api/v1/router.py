from fastapi import APIRouter
from src.api.v1.endpoints import (
    auth, health, users, books, library, community, 
    loan_requests, loans, messages, ai, admin, covers, websocket
)

api_router = APIRouter()

api_router.include_router(auth.router)
api_router.include_router(health.router)
api_router.include_router(users.router)
api_router.include_router(books.router)
api_router.include_router(library.router)
api_router.include_router(community.router)
api_router.include_router(loan_requests.router)
api_router.include_router(loans.router)
api_router.include_router(messages.router)
api_router.include_router(ai.router)
api_router.include_router(admin.router)
api_router.include_router(covers.router)
api_router.include_router(websocket.router)
