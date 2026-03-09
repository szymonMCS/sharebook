from fastapi import APIRouter

from src.api.v1.endpoints.auth import auth_router, users_router
from src.api.v1.endpoints.books import books_router, community_router, covers_router
from src.api.v1.endpoints.loans import loans_router, loan_requests_router, messages_router
from src.api.v1.endpoints.system import health_router, ai_router, websocket_router
from src.api.v1.endpoints import library, admin

api_router = APIRouter()

api_router.include_router(auth_router)
api_router.include_router(users_router)
api_router.include_router(health_router)
api_router.include_router(books_router)
api_router.include_router(library.router)
api_router.include_router(community_router)
api_router.include_router(loan_requests_router)
api_router.include_router(loans_router)
api_router.include_router(messages_router)
api_router.include_router(ai_router)
api_router.include_router(admin.router, prefix="/admin")
api_router.include_router(covers_router)
api_router.include_router(websocket_router)
