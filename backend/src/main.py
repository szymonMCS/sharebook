import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from database.config import init_db, close_db
from src.api.v1.router import api_router
from src.services.cover import get_cover_service
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
    
    try:
        cover_service = await get_cover_service()
        await cover_service.close()
        print("Cover service connections closed")
    except Exception as e:
        logger.warning(f"Error closing cover service: {e}")
    
    print("Goodbye!")

limiter = Limiter(key_func=get_remote_address)

app = FastAPI(
    title="ShareBook API",
    description="API dla systemu wymiany książek między użytkownikami",
    version="0.1.0",
    
    lifespan=lifespan,
    
    docs_url="/docs",    
    redoc_url="/redoc",  
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
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
    logger.warning(f"ShareBookException: {exc.code} - {exc.message}")
    headers = {}
    if exc.status_code == 401:
        headers["WWW-Authenticate"] = "Bearer"
    return JSONResponse(
        status_code=exc.status_code,
        headers=headers,
        content=APIResponse.error(
            message=exc.message,
            meta={"code": exc.code, "details": exc.details}
        ).model_dump()
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    logger.exception(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content=APIResponse.error(
            message="Internal server error"
        ).model_dump()
    )

@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    logger.warning(f"Rate limit exceeded: {request.client.host}")
    return JSONResponse(
        status_code=429,
        content=APIResponse.error(
            message="Too many login attempts. Please try again later."
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