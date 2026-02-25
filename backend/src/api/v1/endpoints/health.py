from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from src.api.deps import get_db

router = APIRouter(prefix="/health", tags=["health"])

@router.get("", status_code=status.HTTP_200_OK)
async def health_check():
    return {
        "status": "healthy",
        "message": "ShareBook API is running",
    }

@router.get("/db", status_code=status.HTTP_200_OK)
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
            return {
                "status": "unhealthy",
                "database": "error",
                "message": "Unexpected response from database",
            }
    except Exception as e:
        print(f"Database health check failed: {e}")
        
        from fastapi import HTTPException
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Database connection failed: {str(e)}",
        )