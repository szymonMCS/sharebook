from fastapi import APIRouter
from src.api.v1.endpoints.library.routes import router as library_router
from src.api.v1.endpoints.library import browse, management

router = APIRouter()

router.include_router(library_router, prefix="/my-books", tags=["library"])
router.include_router(management.management_router, prefix="/my-books", tags=["library"])
