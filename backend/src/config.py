from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = Field(..., pattern=r"^postgresql\+asyncpg://", description="PostgreSQL async connection string")
    # Security - wymagane z env
    SECRET_KEY: str = Field(..., min_length=32, description="Secret key for JWT signing (min 32 chars)")
    DEBUG: bool = Field(default=False, description="Debug mode - disable in production")
    # JWT Settings
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30, ge=1, le=1440)
    REFRESH_TOKEN_EXPIRE_DAYS: int = Field(default=7, ge=1, le=30)
    ALGORITHM: str = Field(default="HS256", pattern=r"^HS(256|384|512)$")
    # OpenAI
    OPENAI_API_KEY: str = Field(default="", description="OpenAI API key for AI features")
    OPENAI_EMBEDDING_MODEL: str = Field(default="text-embedding-3-small")
    OPENAI_CHAT_MODEL: str = Field(default="gpt-4o-mini")
    # RAG Settings
    CHUNK_SIZE: int = Field(default=1000, ge=100, le=5000)
    CHUNK_OVERLAP: int = Field(default=200, ge=0, le=1000)
    KNOWLEDGE_BASE_PATH: str = Field(default="data/knowledge_base.md")
    # AI Service Settings
    AI_MAX_TOKENS: int = Field(default=500, ge=100, le=2000)
    AI_MAX_CONTEXT_CHUNKS: int = Field(default=5, ge=1, le=20)
    AI_MAX_HISTORY_MESSAGES: int = Field(default=10, ge=1, le=50)
    # Cover System
    COVERS_PATH: str = Field(default="database/covers")
    MAX_COVER_SIZE_MB: int = Field(default=5, ge=1, le=50)
    ALLOWED_COVER_TYPES: set[str] = Field(
        default={"image/jpeg", "image/jpg", "image/png", "image/webp"}
    )

    model_config = SettingsConfigDict(
        env_file="../.env",
        extra="ignore"
    )


settings = Settings()
