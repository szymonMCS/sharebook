from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.deps import get_db, get_current_active_user, get_current_active_admin
from src.services.ai import VectorService, AIService
from database.models import User

router = APIRouter(prefix="/ai", tags=["ai"])

class ChatRequest(BaseModel):
    message: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "message": "Poleć mi fantasy z magią"
            }
        }


class ChatResponse(BaseModel):
    success: bool
    answer: str
    sources: list
    model_used: str


class SyncResponse(BaseModel):
    success: bool
    total_books: int
    indexed_books: int
    total_chunks: int
    errors: list


class HealthResponse(BaseModel):
    status: str
    vector_db: dict


@router.post("/chat", response_model=ChatResponse)
async def chat_with_ai(request: ChatRequest, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    try:
        vector_service = VectorService(db)
        ai_service = AIService(vector_service)
        
        result = await ai_service.get_recommendation(request.message)
        
        return ChatResponse(
            success=True,
            answer=result["answer"],
            sources=result["sources"],
            model_used=result["model_used"]
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing AI request: {str(e)}"
        )


@router.get("/health", response_model=HealthResponse)
async def ai_health_check(db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    try:
        vector_service = VectorService(db)
        stats = await vector_service.get_stats()
        
        return HealthResponse(
            status="healthy",
            vector_db=stats
        )
    
    except Exception as e:
        return HealthResponse(
            status="unhealthy",
            vector_db={"error": str(e)}
        )


@router.post("/sync", response_model=SyncResponse)
async def sync_vector_db(db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_active_admin)):
    try:
        vector_service = VectorService(db)
        stats = await vector_service.sync_all_books()
        
        return SyncResponse(
            success=True,
            **stats
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error syncing vector database: {str(e)}"
        )
