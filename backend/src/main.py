from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database.config import init_db, close_db
from src.api.v1.router import api_router
from src.config import settings

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

@app.get("/")
async def root():
    return {
        "name": "ShareBook API",
        "version": "0.1.0",
        "docs": "/docs",
        "health": "/api/v1/health",
    }