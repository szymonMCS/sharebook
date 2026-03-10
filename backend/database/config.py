from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy import text
from src.config import settings

DATABASE_URL = settings.DATABASE_URL

engine: AsyncEngine = create_async_engine(
    DATABASE_URL,
    echo=False,
    future=True,
    pool_size=10,         
    max_overflow=20,       
    pool_timeout=30,      
    pool_recycle=1800,      
    pool_pre_ping=True,   
)

AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False, autocommit=False,autoflush=False)

Base = declarative_base()

async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

async def get_async_session():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

async def check_database_exists() -> bool:
    try:
        async with engine.connect() as conn:
            result = await conn.execute(text("SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'users')"))
            return result.scalar()
    except Exception:
        return False

async def init_db():
    async with engine.begin() as conn:
        try:
            await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
        except Exception as e:
            print(f"Warning: Could not create pgvector extension: {e}")
            print("AI features may not work properly.")
        await conn.run_sync(Base.metadata.create_all)
    print("[OK] Database initialized (PostgreSQL)")

async def reset_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    print("[OK] Database reset complete")

async def close_db():
    await engine.dispose()
    print("[OK] Database connections closed")

async def get_db_status() -> dict:
    try:
        async with engine.connect() as conn:
            result = await conn.execute(text("SELECT version()"))
            version = result.scalar()
            tables_exist = await check_database_exists()
            return {
                "connected": True,
                "type": "PostgreSQL",
                "version": version,
                "tables_created": tables_exist
            }
    except Exception as e:
        return {
            "connected": False,
            "type": "Unknown",
            "error": str(e)
        }