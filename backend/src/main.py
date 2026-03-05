import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from database.config import init_db, close_db
from src.api.v1.router import api_router
from src.config import settings
from src.core.exceptions import ShareBookException
from src.core.response import APIResponse

logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Starting up ShareBook API...")
    print(f"Debug mode: {settings.DEBUG}")
    print(f"Database: {settings.DATABASE_URL.split('@')[-1]}")
    
    try:
        await init_db()
        print("Database initialized - tables created (if not existed)")
    except Exception as e:
        print(f"Database initialization failed: {e}")
        print("   Check if PostgreSQL is running: docker-compose ps")
        raise
    
    yield
    
    print("Shutting down ShareBook API...")
    
    await close_db()
    print("Database connections closed")
    
    print("Goodbye!")

app = FastAPI(
    title="ShareBook API",
    description="API dla systemu wymiany książek między użytkownikami",
    version="0.1.0",
    
    lifespan=lifespan,
    
    docs_url="/docs",    
    redoc_url="/redoc",  
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  
        "http://localhost:3000",  
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api/v1")

app.mount("/covers", StaticFiles(directory=settings.COVERS_PATH), name="covers")

@app.exception_handler(ShareBookException)
async def sharebook_exception_handler(request: Request, exc: ShareBookException):
    """Globalny handler dla wyjątków ShareBookException."""
    logger.warning(f"ShareBookException: {exc.code} - {exc.message}")
    return JSONResponse(
        status_code=exc.status_code,
        content=APIResponse.error(
            message=exc.message,
            meta={"code": exc.code, "details": exc.details}
        ).model_dump()
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Globalny handler dla nieobsłużonych wyjątków."""
    logger.exception(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content=APIResponse.error(
            message="Internal server error" if not settings.DEBUG else str(exc)
        ).model_dump()
    )


@app.get("/")
async def root():
    return {
        "name": "ShareBook API",
        "version": "0.1.0",
        "docs": "/docs",
        "health": "/api/v1/health",
    }