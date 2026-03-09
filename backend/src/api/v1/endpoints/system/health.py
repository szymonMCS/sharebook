from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from src.api.deps import get_db
from src.core.exceptions import ServiceUnavailableException

router = APIRouter(prefix="/health", tags=["health"])


@router.get("")
async def health_check():
    return {
        "status": "healthy",
        "message": "ShareBook API is running",
    }


@router.get("/db")
async def health_check_db(db: AsyncSession = Depends(get_db)):
    try:
        result = await db.execute(text("SELECT 1"))
        row = result.scalar()

        if row == 1:
            return {
                "status": "healthy",
                "database": "connected",
                "message": "PostgreSQL connection OK",
            }
        else:
            raise ServiceUnavailableException("Unexpected response from database")
    except Exception as e:
        raise ServiceUnavailableException(f"Database connection failed: {str(e)}")
