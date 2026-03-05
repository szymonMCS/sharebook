from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql+asyncpg://user:pass@localhost/sharebook"
    SECRET_KEY: str = "your-secret-key-change-in-production"
    DEBUG: bool = True
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    ALGORITHM: str = "HS256"
    OPENAI_API_KEY: str = ""
    OPENAI_EMBEDDING_MODEL: str = "text-embedding-3-small"
    OPENAI_CHAT_MODEL: str = "gpt-4o-mini"
    CHUNK_SIZE: int = 1000
    CHUNK_OVERLAP: int = 200
    KNOWLEDGE_BASE_PATH: str = "data/knowledge_base.md"
    GOOGLE_BOOKS_API_KEY: str = ""
    GOOGLE_BOOKS_API_URL: str = "https://www.googleapis.com/books/v1/volumes"
    GOOGLE_BOOKS_TIMEOUT: int = 10
    
    COVERS_PATH: str = "covers"
    MAX_COVER_SIZE_MB: int = 5
    ALLOWED_COVER_TYPES: list = ["image/jpeg", "image/jpg", "image/png", "image/webp"]

    model_config = SettingsConfigDict(
        env_file="../.env",
        extra="ignore"
    )

settings = Settings()